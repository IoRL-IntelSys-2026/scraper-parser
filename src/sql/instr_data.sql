-- Describes the target document's file type.
insert into doc_type (kind) values
  ('html'),
  ('pdf');

-- Links that lead to the required document.
insert into doc_link (link) values
  ('https://admission.rudn.ru/undergraduate/'),
  ('https://admission.rudn.ru/master/'),
  ('https://admission.rudn.ru/postgraduate/'),
  ('https://admission.rudn.ru/internship/'),
  ('https://admission.rudn.ru/undergraduate/timing/'),
  ('https://admission.rudn.ru/master/timing/'),
  ('https://admission.rudn.ru/postgraduate/timing/'),
  ('https://admission.rudn.ru/internship/timing/'),
  ('https://www.rudn.ru/science/dad/doctorantura/');

insert into document (idx, link, kind) values
  (1, 'https://admission.rudn.ru/undergraduate/timing/', 'pdf'),
  (2, 'https://admission.rudn.ru/master/timing/', 'pdf'),
  (3, 'https://admission.rudn.ru/postgraduate/timing/', 'pdf'),
  (4, 'https://admission.rudn.ru/internship/timing/', 'pdf'),
  (5, 'https://admission.rudn.ru/undergraduate/', 'html'),
  (6, 'https://admission.rudn.ru/master/', 'html'),
  (7, 'https://admission.rudn.ru/postgraduate/', 'html'),
  (8, 'https://admission.rudn.ru/internship/', 'html'),
  (9, 'https://www.rudn.ru/science/dad/doctorantura/', 'html');

/*
 * Instruction descriptions:
 *  - click_first: Click on the first (or only) HTML element
 *    with the specified attributes.
 *  - extract_subtree: Extract the element with the specified
 *    attributes and all of its children and save them as an
 *    HTML document.
 *  - if_matches: If an element with these attributes exists,
 *    proceed to the next instruction, otherwise jump to
 *    `branch_tgt`. Requires the `branch_tgt` attribute
 *    to be set.
 *  - download_target: Download the document pointed to
 *    by the element with these attributes, similar to
 *    the "Save link as..." action in most browsers.
 */
insert into instruction (title) values
  ('click_first'),
  ('extract_subtree'),
  ('if_matches'),
  ('download_target');

/*
 * Attribute descriptions:
 *  - branch-tgt: used to specify a step for branch instructions.
 *  - tag: The HTML element's tag.
 *  - id: the element's (hopefully unique) id.
 *  - class: one or more element classes separated by spaces.
 *  - text: The element's text node, e.g. the "Hi" in <h1>Hi</h1>.
 * Attributes not listed here have no special meaning and are used
 * to select elements.
 */
insert into attribute (attr) values
  ('branch-tgt'),
  ('tag'),
  ('id'),
  ('class'),
  ('text'),
  ('data-editor');

insert into doc_inst values
  (1, 1, 'download_target'),
  (2, 1, 'download_target'),
  (3, 1, 'download_target'),
  (4, 1, 'download_target'),
  (9, 1, 'extract_subtree');

insert into inst_attr values
  (1, 1, 'tag', 'a'),
  (1, 1, 'data-editor', 'pdf.link'),
  (2, 1, 'tag', 'a'),
  (2, 1, 'data-editor', 'pdf.link'),
  (3, 1, 'tag', 'a'),
  (3, 1, 'data-editor', 'pdf.link'),
  (4, 1, 'tag', 'a'),
  (4, 1, 'data-editor', 'pdf.link'),
  (9, 1, 'tag', 'div'),
  (9, 1, 'class', 'article__one-inner');
