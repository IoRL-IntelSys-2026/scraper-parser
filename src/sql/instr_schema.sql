pragma journal_mode=WAL;
pragma foreign_keys=ON;

-- Links to pages where the document can be found.
create table if not exists doc_link (
  link text not null unique primary key
    on conflict rollback check (link like 'https://%/')
) strict, without rowid;

/*
 * Describes the document's file type. This is an enum, check
 * the comments in the data file for the meaning of each value.
 */
create table if not exists doc_type (
  kind integer not null unique primary key on conflict rollback check (kind > 0)
) strict;

/*
 * Combines links with document types. Intentionally allows duplicates
 * for the case when multiple documents of the same type on one page
 * require different steps to extract them.
 */
create table if not exists document (
  idx integer not null unique primary key on conflict rollback,
  link text not null references doc_link (link)
    on update cascade
    on delete restrict,
  kind integer not null references doc_type (kind)
    on update cascade
    on delete restrict
) strict;

/*
 * Describes actions that can be performed by the web scraper,
 * such as clicking on links or buttons. This is an enum, check
 * the comments in the data file for the meaning of each value.
 */
create table if not exists instruction (
  inst integer not null unique primary key on conflict rollback check (inst > 0)
) strict;

-- Describes which actions need to be performed and their order.
create table if not exists doc_inst (
  doc integer not null references document (idx)
    on update cascade
    on delete cascade,
  step integer not null,
  inst integer not null references instruction (inst),
  primary key (doc, step) on conflict rollback
) strict, without rowid;

/*
 * Attributes are used to provide information necessary to
 * execute an instruction, in other words, they are like
 * function arguments.
 */
create table if not exists attribute (
  attr text not null unique primary key on conflict rollback
) strict, without rowid;

-- Extends intructions with attributes.
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
