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
