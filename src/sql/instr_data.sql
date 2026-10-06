-- Ссылки на документы
insert into doc_link values
  ('https://admission.rudn.ru/undergraduate/'),
  ('https://admission.rudn.ru/master/'),
  ('https://admission.rudn.ru/postgraduate/'),
  ('https://admission.rudn.ru/internship/'),
  ('https://admission.rudn.ru/undergraduate/timing/'),
  ('https://admission.rudn.ru/master/timing/'),
  ('https://admission.rudn.ru/postgraduate/timing/'),
  ('https://admission.rudn.ru/internship/timing/'),
  ('https://www.rudn.ru/science/dad/doctorantura/');

/*
 * Конечные типы документов:
 *  0 - PDF,
 *  1 - HTML.
 */
insert into document (url, kind) values
  ('https://admission.rudn.ru/undergraduate/timing/', 0),
  ('https://admission.rudn.ru/master/timing/', 0),
  ('https://admission.rudn.ru/postgraduate/timing/', 0),
  ('https://admission.rudn.ru/internship/timing/', 0),
  ('https://admission.rudn.ru/undergraduate/', 1),
  ('https://admission.rudn.ru/master/', 1),
  ('https://admission.rudn.ru/postgraduate/', 1),
  ('https://admission.rudn.ru/internship/', 1),
  ('https://www.rudn.ru/science/dad/doctorantura/', 1);
  
