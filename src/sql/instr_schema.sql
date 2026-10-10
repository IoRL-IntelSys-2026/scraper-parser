pragma journal_mode=WAL;
pragma foreign_keys=ON;

-- Links where the document can be found.
create table if not exists doc_link (
  link text not null unique primary key
    on conflict rollback check (link like 'https://%/')
) strict, without rowid;

/*
 * Describes the document's file type. Consists only of
 * the file extension, since the level of detail provided
 * by a full MIME type is unlikely to be necessary for
 * fetching documents.
 */
create table if not exists doc_type (
  kind text not null unique primary key
    on conflict rollback check (ltrim(kind, 'abcdefghijklmnopqrstuvwxyz') = '')
) strict, without rowid;

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
  kind text not null references doc_type (kind)
    on update cascade
    on delete restrict
) strict;

/*
 * Describes actions that can be performed by the web scraper,
 * such as clicking on links or buttons.
 */
create table if not exists instruction (
  title text not null unique primary key
    on conflict rollback check (ltrim(title, 'abcdefghijklmnopqrstuvwxyz_') = '')
) strict, without rowid;

-- Describes which actions need to be performed and their order.
create table if not exists doc_inst (
  doc integer not null references document (idx)
    on update cascade
    on delete cascade,
  step integer not null,
  inst text not null references instruction (title),
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
