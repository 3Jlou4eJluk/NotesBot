# NotesBot

## О проекте
Данный бот был сделан для того, чтобы раскрыть полный потенциал неожиданных инсайтов. Решение призвано упростить сохранение заметок, а так же предоставить удобные инструменты для работы с мыслями, которые основаны на современных NLP-методах.


## Устройство бота
Состоит из двух частей: сам бот, написанный на aiogram(3beta) в асинхронном стиле, а также FastAPI сервер, на котором проводятся все вычисления. Подобное устройство позволяет боту не зависать в моменты выполнения ML-расчётов.

## Функции бота
Рассмотрим действия, которые может выполнять хранитель заметок. Реализованные функции отмечены галочками.

1. ✓ Команды /add_note, /search_note, /get_k_nearest_notes, ...
2. ✓ Меню для более удобного управления заметками
3. ✓ Поиск, основанный на эмбеддингах
4. ✓ Выдача ближайших заметок. На данный момент разрабатывается интерфейс для этой опции. Работает на связке transformers + tSNE
5. Возможность линковки заметок
6. Neural Network linking - обучение на основе настроенных вами связей



## Демонстрация работы

![изображение](https://github.com/3Jlou4eJluk/NotesBot/assets/52838612/6a4d76d6-e35a-49cd-8507-48b14755b6b6)

Нажатие на "добавить заметку":

![Снимок экрана от 2023-08-22 20-40-58](https://github.com/3Jlou4eJluk/NotesBot/assets/52838612/dbfbed80-bcc5-4e95-8a4a-60d6bbc28e47)

![изображение](https://github.com/3Jlou4eJluk/NotesBot/assets/52838612/36d4b25a-39b2-40e8-a23d-2f2853c73c15)

Хорошо, теперь имеем 2 заметки, у каждой есть индивидуальный id в системе. Функция семантического поиска позволяет найти подходящую:

![изображение](https://github.com/3Jlou4eJluk/NotesBot/assets/52838612/f5b0636e-f610-4f6f-940b-97802a8287af)

Первая добавленная нами заметка представляет из себя запись в таблице с note_id = 0. Вторая - с note_id = 1. Как видно, мы смогли без особых усилий отделить первое от второго.

Теперь рассмотрим "Удалить заметку":

![Снимок экрана от 2023-08-22 20-55-16](https://github.com/3Jlou4eJluk/NotesBot/assets/52838612/92ea00ed-23b6-491e-8b0f-b31fd3674a2c)





