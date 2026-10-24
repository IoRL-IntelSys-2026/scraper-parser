-- 1. Insert the pre-defined broad topics requested by the team layout
insert into topic (num) values
  (1), -- Общежитие
  (2), -- Питание
  (3), -- Приемная комиссия (Placeholder for Admissions)
  (4); -- Общая информация (Placeholder for General Help)

-- Describes the target document's file type.
insert into doc_type (kind) values
  (1), -- HTML
  (2); -- PDF

-- Links that lead to the required document with broad topics attached.
insert into doc_link (link, topic) values
  ('https://admission.rudn.ru/undergraduate/', 3), -- поступление бакалавриат/специалитет
  ('https://admission.rudn.ru/master/', 3), -- поступление магситратура
  ('https://admission.rudn.ru/postgraduate/', 3), -- поступление аспирантура
  ('https://admission.rudn.ru/internship/', 3), -- поступление ординатура
  ('https://admission.rudn.ru/undergraduate/timing/', 3), -- сроки приема бакалавриат/специалитет
  ('https://admission.rudn.ru/master/timing/', 3), -- сроки приема магистратура
  ('https://admission.rudn.ru/postgraduate/timing/', 3), -- сроки приема аспирантура
  ('https://admission.rudn.ru/internship/timing/', 3), -- сроки приема ординатура
  ('https://www.rudn.ru/science/dad/doctorantura/', 3), -- докторантура
  /*
   * сведения о трудоустройстве выпускников в виде численности
   * трудоустроенных выпускников прошлого учебного года
   */
  ('https://www.rudn.ru/sveden/education/employment/', 4),
  ('https://www.rudn.ru/sveden/catering/', 2), -- организация питания в образовательной организации
  ('https://www.rudn.ru/life/accomodation/', 1), -- проживание
  ('https://www.rudn.ru/life/multifunctional-center/', 4), -- мфц
  ('https://handbook.rudn.ru/help/social.html', 4), -- социальная карта
  ('https://handbook.rudn.ru/help/mail.html', 4), -- корпоративная почта
  ('https://handbook.rudn.ru/help/id.html', 4), -- индивидуальный цифровой ключ (RUDN ID)
  ('https://handbook.rudn.ru/help/passport.html', 4), -- Паспортно-визовый, миграционный и регистрационный учет
  ('https://handbook.rudn.ru/help/war.html', 4), -- Военно-учетный отдел (для студентов из РФ)
  ('https://handbook.rudn.ru/help/duplicate.html', 4), -- Справки и дубликаты документов
  ('https://handbook.rudn.ru/help/campus.html', 4); -- оформление карты
  
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
  (10, 'https://www.rudn.ru/sveden/education/employment/', 1),
  (11, 'https://www.rudn.ru/sveden/catering/', 1),
  (12, 'https://www.rudn.ru/life/accomodation/', 1),
  (13, 'https://www.rudn.ru/life/multifunctional-center/', 1),
  (14, 'https://handbook.rudn.ru/help/social.html', 1),
  (15, 'https://handbook.rudn.ru/help/mail.html', 1),
  (16, 'https://handbook.rudn.ru/help/id.html', 1),
  (17, 'https://handbook.rudn.ru/help/passport.html', 1),
  (18, 'https://handbook.rudn.ru/help/war.html', 1),
  (19, 'https://handbook.rudn.ru/help/duplicate.html', 1),
  (20, 'https://handbook.rudn.ru/help/campus.html', 1);

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
  (6, 1, 2),
  (7, 1, 2),
  (9, 1, 2),
  (10, 1, 2),
  (11, 1, 2),
  (12, 1, 2),
  (13, 1, 2),
  /*
   * Requires two steps since the required elements don't have
   * a common ancestor.
   */
  (14, 1, 2),
  (14, 2, 2);

insert into inst_attr (doc, step, kind, val) values
  (1, 1, 'tag', 'a'),
  (1, 1, 'data-editor', 'pdf.link'),
  (2, 1, 'tag', 'a'),
  (2, 1, 'data-editor', 'pdf.link'),
  (3, 1, 'tag', 'a'),
  (3, 1, 'data-editor', 'pdf.link'),
  (4, 1, 'tag', 'a'),
  (4, 1, 'data-editor', 'pdf.link'),
  (6, 1, 'tag', 'div'),
  (6, 1, 'class', 'container'),
  (7, 1, 'tag', 'div'),
  (7, 1, 'class', 'container'),
  (9, 1, 'tag', 'div'),
  (9, 1, 'class', 'article__one-inner'),
  (10, 1, 'tag', 'div'),
  (10, 1, 'id', 'vikon-content'),
  (11, 1, 'tag', 'div'),
  (11, 1, 'id', 'vikon-content'),
  (12, 1, 'tag', 'div'),
  (12, 1, 'class', 'acc-page'),
  (13, 1, 'tag', 'div'),
  (13, 1, 'class', 'content'),
  (14, 1, 'tag', 'section'),
  (14, 1, 'class', 'page-subtitle-help'),
  (14, 2, 'tag', 'section'),
  (14, 2, 'class', 'main');
