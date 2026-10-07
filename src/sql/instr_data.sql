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

insert into document (url, kind) values
  ('https://admission.rudn.ru/undergraduate/timing/', 'pdf'),
  ('https://admission.rudn.ru/master/timing/', 'pdf'),
  ('https://admission.rudn.ru/postgraduate/timing/', 'pdf'),
  ('https://admission.rudn.ru/internship/timing/', 'pdf'),
  ('https://admission.rudn.ru/undergraduate/', 'html'),
  ('https://admission.rudn.ru/master/', 'html'),
  ('https://admission.rudn.ru/postgraduate/', 'html'),
  ('https://admission.rudn.ru/internship/', 'html'),
  ('https://www.rudn.ru/science/dad/doctorantura/', 'html');

/*
 * Описания для инструкций:
 *  - click_first: нажать на первый элемент с указанными
 *   атрибутами.
 *  - extract_subtree: Извлечь элемент с этими атрибутами
 *   и все элементы внутри него и сохранить их.
 *  - if_matches: Должно иметь атрибут "target". Если
 *   элемент с такими атрибутами есть, то перейти к
 *   следующей инструкции. Иначе перейти к номеру
 *   инструкции "target".
 */
insert into instruction (title) values
  ('click_first'),
  ('extract_subtree'),
  ('if_matches');

/*
 * Описания для тегов:
 *  - target: используется разными инструкциями. См. описание
 *   инструкции для определения target.
 *  - tag: HTML-тег элемента.
 *  - id: (уникальный) атрибут "id" HTML-элемента.
 *  - class: атрибут "class" (один или несколько через пробел)
 *   HTML-элемента.
 *  - text: Текст внутри HTML-элемента, т.е. "Hi" для <h1>Hi</h1>.
 */
insert into attribute (attr) values
  ('target'),
  ('tag'),
  ('id'),
  ('class'),
  ('text');
