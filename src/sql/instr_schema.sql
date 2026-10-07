pragma journal_mode=WAL;
pragma foreign_keys=ON;

create table if not exists doc_link (
  link text not null unique primary key
    on conflict rollback check (like 'https://%/')
) strict, without rowid;

create table if not exists doc_type (
  kind text not null unique primary key
    on conflict rollback check (ltrim(kind, 'abcdefghijklmnopqrstuvwxyz') = '')
) strict, without rowid;

create table if not exists document (
  idx integer not null unique primary key on conflict rollback autoincrement,
  link text not null references doc_link (link)
    on update cascade
    on delete restrict,
  kind text not null references doc_type (kind)
    on update cascade
    on delete restrict
) strict;

create table if not exists instruction (
  title text not null unique primary key
    on conflict rollback check (ltrim(title, 'abcdefghijklmnopqrstuvwxyz') = '')
) strict, without rowid;

create table if not exists doc_inst (
  doc integer not null references document (idx)
    on update cascade
    on delete cascade,
  step integer not null,
  inst text not null references instruction (title),
  primary key (doc, step) on conflict rollback
) strict, without rowid;

create table if not exists attribute (
  attr text not null unique primary key on conflict rollback
) strict, without rowid;

create table if not exists inst_attr (
  doc integer not null,
  step integer not null,
  kind text not null references attribute (attr)
    on update cascade
    on delete restrict,
  val text not null,
  primary key (doc, step, kind) on conflict rollback,
  foreign key (doc, step) references doc_inst (doc, step)
    on update cascade
    on delete cascade
) strict, without rowid;

vacuum;
pragma optimize;
