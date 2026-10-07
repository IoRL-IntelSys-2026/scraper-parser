-- Какие типы документов в итоге?
insert into doc_type (kind) values
  ('html'),
  ('pdf');

-- Ссылки на документы
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
 * Описания для инструкций:
 *  - click_first: нажать на первый элемент с указанными
 *   атрибутами. (обычно единственный)
 *  - extract_subtree: Извлечь элемент с этими атрибутами
 *   и все элементы внутри него и сохранить их.
 *  - if_matches: Должно иметь атрибут "branch-tgt". Если
 *   элемент с такими атрибутами есть, то перейти к
 *   следующей инструкции. Иначе перейти к номеру
 *   инструкции "branch-tgt".
 *  - download_target: скачать то, что находится за ссылкой
 *   совпадающего по атрибутам элемента, наподобие "Сохранить
 *   ссылку как..." в браузере.
 */
insert into instruction (title) values
  ('click_first'),
  ('extract_subtree'),
  ('if_matches'),
  ('download_target');

/*
 * Описания для тегов:
 *  - branch-tgt: используется разными инструкциями. См. описание
 *   инструкции для определения branch-tgt.
 *  - tag: HTML-тег элемента.
 *  - id: (уникальный) атрибут "id" HTML-элемента.
 *  - class: атрибут "class" (один или несколько через пробел)
 *   HTML-элемента.
 *  - text: Текст внутри HTML-элемента, т.е. "Hi" для <h1>Hi</h1>.
 * Атрибуты, у которых нет описания, используются элементами на
 * странице, и их нужно использовать для поиска нужного элемента.
 */
insert into attribute (attr) values
  ('branch-tgt'),
  ('tag'),
  ('id'),
  ('class'),
  ('text'),
  ('data-editor');

-- Документы 1-4: так как это кнопка для загрузки
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
