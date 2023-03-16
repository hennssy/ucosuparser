# Schedule parser for University College, Orenburg

<b>That is finally version of the VK bot, which parses the schedule from the site uc.osu.ru. This project deployed on Yandex Cloud Functions in conjunction with Yandex Cloud Database (AWS boto3.dynamodb) and Yandex Cloud Message Queue. Bot works without the participation of a local computer and failsafe. It means if any error occured during script working, message with that error will be logged & skipped.

For security reasons, the personal data of the developer's config and virtual environment variables, as well as the secret keys of the VK API are hidden.</b>

# Парсер расписания для Университетского Колледжа г. Оренбурга

<b>Это итоговая версия ВК бота, который парсит расписание с сайта uc.osu.ru. Данный проект развернут на сервисе Yandex Cloud Functions в связке с другими сервисами платформы - Yandex Cloud Database (с использованием библиотеки boto3 и хэш-таблиц dynamodb) и очереди сообщений Yandex Cloud Message Queue. Бот работает без участия локального компьютера и является отказоустойчивым, т.е при возникновении ошибки во время работы программы, сообщение с ошибкой будет сохранено и пропущено.
  
Из соображений безопасности, данные конфигурации разработчика и переменных виртуального окружения, а также секретные ключи API Вконтакте скрыты.</b>
