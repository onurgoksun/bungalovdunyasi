-- =====================================================================
--  Bungalov Dünyası · üyelik, tesis ilanları, favoriler
--  Supabase SQL Editor'de bir kez çalıştırılır. Tekrar çalıştırmak zararsızdır.
--  Uygulamanın (Bungalov Yönetim) tablolarına DOKUNMAZ; site üyeleri uygulama
--  verilerini göremez (o tablolar my_facility() ile korunur).
-- =====================================================================

-- ---------------------------------------------------------------- Üye profili
create table if not exists public.site_profiles (
  id            uuid primary key references auth.users(id) on delete cascade,
  kind          text not null check (kind in ('kurumsal', 'kisisel')),
  full_name     text not null default '',
  phone         text not null default '',
  company       text not null default '',       -- kurumsal: işletme / tesis adları
  kvkk_ok_at    timestamptz,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
alter table public.site_profiles enable row level security;
revoke all on public.site_profiles from anon;
grant select, insert, update on public.site_profiles to authenticated;

drop policy if exists sp_own_select on public.site_profiles;
create policy sp_own_select on public.site_profiles for select to authenticated using (id = auth.uid());
drop policy if exists sp_own_insert on public.site_profiles;
create policy sp_own_insert on public.site_profiles for insert to authenticated with check (id = auth.uid());
drop policy if exists sp_own_update on public.site_profiles;
create policy sp_own_update on public.site_profiles for update to authenticated using (id = auth.uid()) with check (id = auth.uid());

-- Site yöneticileri (ilanları kaldırabilir)
create table if not exists public.site_admins (
  user_id uuid primary key references auth.users(id) on delete cascade
);
alter table public.site_admins enable row level security;
revoke all on public.site_admins from anon, authenticated;

create or replace function public.is_site_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.site_admins where user_id = auth.uid())
$$;
grant execute on function public.is_site_admin() to authenticated;

create or replace function public.is_kurumsal() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.site_profiles where id = auth.uid() and kind = 'kurumsal')
$$;
grant execute on function public.is_kurumsal() to authenticated;

-- ---------------------------------------------------------------- Tesis ilanları
create table if not exists public.listings (
  id            uuid primary key default gen_random_uuid(),
  owner         uuid not null references auth.users(id) on delete cascade default auth.uid(),
  slug          text not null unique check (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$' and length(slug) between 3 and 80),
  status        text not null default 'yayinda' check (status in ('yayinda', 'taslak', 'kaldirildi')),
  name          text not null check (length(trim(name)) between 2 and 80),
  summary       text not null default '' check (length(summary) <= 300),
  description   text not null default '' check (length(description) <= 6000),
  district      text not null default 'Sapanca',
  neighborhood  text not null default '',
  address       text not null default '' check (length(address) <= 300),
  units         int  check (units is null or units between 1 and 200),
  capacity      text not null default '' check (length(capacity) <= 80),
  beds          text not null default '' check (length(beds) <= 120),
  amenities     text[] not null default '{}',
  pets          text not null default 'sor' check (pets in ('evet', 'hayir', 'sor')),
  checkin       text not null default '' check (length(checkin) <= 10),
  checkout      text not null default '' check (length(checkout) <= 10),
  rules         text not null default '' check (length(rules) <= 2000),
  phone         text not null default '' check (length(phone) <= 30),
  whatsapp      text not null default '' check (length(whatsapp) <= 30),
  website       text not null default '' check (length(website) <= 200),
  booking_url   text not null default '' check (length(booking_url) <= 300),
  instagram     text not null default '' check (length(instagram) <= 100),
  photos        jsonb not null default '[]'::jsonb,   -- [{path, alt}] ilk eleman kapak
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  removed_reason text not null default ''
);
create index if not exists listings_owner_idx on public.listings (owner);
create index if not exists listings_status_idx on public.listings (status, updated_at desc);
alter table public.listings enable row level security;
grant select on public.listings to anon, authenticated;
grant insert, update, delete on public.listings to authenticated;

drop policy if exists l_public_read on public.listings;
create policy l_public_read on public.listings for select to anon, authenticated
  using (status = 'yayinda' or owner = auth.uid() or public.is_site_admin());
drop policy if exists l_owner_insert on public.listings;
create policy l_owner_insert on public.listings for insert to authenticated
  with check (owner = auth.uid() and public.is_kurumsal() and status in ('yayinda', 'taslak'));
drop policy if exists l_owner_update on public.listings;
create policy l_owner_update on public.listings for update to authenticated
  using (owner = auth.uid() or public.is_site_admin())
  with check ((owner = auth.uid() and status in ('yayinda', 'taslak')) or public.is_site_admin());
drop policy if exists l_owner_delete on public.listings;
create policy l_owner_delete on public.listings for delete to authenticated
  using (owner = auth.uid() or public.is_site_admin());

-- Yönetici kaldırdıysa sahibi tekrar yayına alamasın; zaman damgası
create or replace function public.listings_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  new.updated_at := now();
  if tg_op = 'UPDATE' then
    new.owner := old.owner;
    new.created_at := old.created_at;
    if old.status = 'kaldirildi' and not public.is_site_admin() then
      new.status := 'kaldirildi';
      new.removed_reason := old.removed_reason;
    end if;
    if not public.is_site_admin() then
      new.removed_reason := old.removed_reason;
    end if;
  end if;
  if jsonb_typeof(new.photos) <> 'array' or jsonb_array_length(new.photos) > 20 then
    raise exception 'En fazla 20 fotoğraf eklenebilir';
  end if;
  if array_length(new.amenities, 1) > 40 then
    raise exception 'Çok fazla olanak seçildi';
  end if;
  return new;
end $$;
drop trigger if exists listings_guard_t on public.listings;
create trigger listings_guard_t before insert or update on public.listings
  for each row execute function public.listings_guard();

-- Kurumsal üye en fazla 20 tesis
create or replace function public.listings_limit() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if (select count(*) from public.listings where owner = new.owner) >= 20 then
    raise exception 'Bir hesaba en fazla 20 tesis eklenebilir';
  end if;
  return new;
end $$;
drop trigger if exists listings_limit_t on public.listings;
create trigger listings_limit_t before insert on public.listings
  for each row execute function public.listings_limit();

-- ---------------------------------------------------------------- Favoriler
create table if not exists public.favorites (
  user_id    uuid not null references auth.users(id) on delete cascade default auth.uid(),
  listing_id uuid not null references public.listings(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (user_id, listing_id)
);
alter table public.favorites enable row level security;
revoke all on public.favorites from anon;
grant select, insert, delete on public.favorites to authenticated;
drop policy if exists fav_own on public.favorites;
create policy fav_own on public.favorites for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());

-- ---------------------------------------------------------------- AI kullanım sayacı
create table if not exists public.ai_usage (
  user_id uuid not null references auth.users(id) on delete cascade,
  day     date not null default (now() at time zone 'Europe/Istanbul')::date,
  n       int  not null default 0,
  primary key (user_id, day)
);
alter table public.ai_usage enable row level security;
revoke all on public.ai_usage from anon, authenticated;

-- Edge Function çağırır (service role ile): kullanım hakkı varsa sayacı artırır
create or replace function public.ai_take(p_user uuid, p_limit int) returns boolean
language plpgsql security definer set search_path = public as $$
declare v int;
begin
  insert into public.ai_usage (user_id) values (p_user) on conflict do nothing;
  update public.ai_usage set n = n + 1
    where user_id = p_user and day = (now() at time zone 'Europe/Istanbul')::date and n < p_limit
    returning n into v;
  return v is not null;
end $$;
revoke execute on function public.ai_take(uuid, int) from public, anon, authenticated;
grant execute on function public.ai_take(uuid, int) to service_role;

-- ---------------------------------------------------------------- Fotoğraf deposu
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('tesis-foto', 'tesis-foto', true, 3145728, array['image/jpeg', 'image/webp', 'image/png'])
on conflict (id) do update set public = true, file_size_limit = 3145728,
  allowed_mime_types = array['image/jpeg', 'image/webp', 'image/png'];

drop policy if exists tf_read on storage.objects;
create policy tf_read on storage.objects for select to anon, authenticated
  using (bucket_id = 'tesis-foto');
drop policy if exists tf_insert on storage.objects;
create policy tf_insert on storage.objects for insert to authenticated
  with check (bucket_id = 'tesis-foto' and (storage.foldername(name))[1] = auth.uid()::text and public.is_kurumsal());
drop policy if exists tf_delete on storage.objects;
create policy tf_delete on storage.objects for delete to authenticated
  using (bucket_id = 'tesis-foto' and ((storage.foldername(name))[1] = auth.uid()::text or public.is_site_admin()));

-- ---------------------------------------------------------------- Türkiye geneli: il alanı (2026-10-14)
alter table public.listings add column if not exists province text not null default '' check (length(province) <= 40);
alter table public.listings alter column district set default '';
