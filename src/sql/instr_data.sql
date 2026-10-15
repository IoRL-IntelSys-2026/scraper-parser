-- Describes the target document's file type.
insert into doc_type (kind) values
  (1), -- HTML
  (2); -- PDF

-- Links that lead to the required document.
insert into doc_link (link) values
  ('https://admission.rudn.ru/undergraduate/'), #поступление бакалавриат/специалитет
  ('https://admission.rudn.ru/master/'), #поступление магситратура
  ('https://admission.rudn.ru/postgraduate/'), #поступлениет аспирантура
  ('https://admission.rudn.ru/internship/'), #поступление ординатура
  ('https://admission.rudn.ru/undergraduate/timing/'), #сроки приема бакалавриат/специалитет
  ('https://admission.rudn.ru/master/timing/'), #сроки приема магистратура
  ('https://admission.rudn.ru/postgraduate/timing/'), #сроки приема аспирантура
  ('https://admission.rudn.ru/internship/timing/'), #сроки приема ординатура
  ('https://www.rudn.ru/science/dad/doctorantura/'), #Докторантура
  ('https://www.rudn.ru/sveden/education/employment/'), #Сведения о трудоустройстве выпускников в виде численности трудоустроенных выпускников прошлого учебного года
  ('https://www.rudn.ru/sveden/catering/'), #Организация питания в образовательной организации
  ('https://www.rudn.ru/life/accomodation'); #проживание
  
  
insert into document (idx, link, kind) values
  (1, 'https://admission.rudn.ru/undergraduate/timing/', 2),
  (2, 'https://admission.rudn.ru/master/timing/', 2),
  (3, 'https://admission.rudn.ru/postgraduate/timing/', 2),
  (4, 'https://admission.rudn.ru/internship/timing/', 2),
  (5, 'https://admission.rudn.ru/undergraduate/', 1),
  (6, 'https://admission.rudn.ru/master/', 1),
  (7, 'https://admission.rudn.ru/postgraduate/', 1),
  (8, 'https://admission.rudn.ru/internship/', 1),
  (9, 'https://www.rudn.ru/science/dad/doctorantura/', 1),
  (10 'https://www.rudn.ru/sveden/education/employment/'1),
  (11 'https://www.rudn.ru/sveden/catering/'1),
  (12 'https://www.rudn.ru/life/accomodation'1);

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
insert into instruction (inst) values
  (1), -- click_first
  (2), -- extract_subtree
  (3), -- if_matches
  (4); -- download_target

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

insert into doc_inst (doc, step, inst) values
  (1, 1, 4),
  (2, 1, 4),
  (3, 1, 4),
  (4, 1, 4),
  (9, 1, 2),
  (10, 1, 2);

insert into inst_attr (doc, step, kind, val) values
  (1, 1, 'tag', 'a'),
  (1, 1, 'data-editor', 'pdf.link'),
  (2, 1, 'tag', 'a'),
  (2, 1, 'data-editor', 'pdf.link'),
  (3, 1, 'tag', 'a'),
  (3, 1, 'data-editor', 'pdf.link'),
  (4, 1, 'tag', 'a'),
  (4, 1, 'data-editor', 'pdf.link'),
  (9, 1, 'tag', 'div'),
  (9, 1, 'class', 'article__one-inner'),
  (10, 1, 'tag', 'div'),
  (10, 1, 'class', 'article__one-inner');
