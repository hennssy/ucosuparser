# Schedule parser for University College, Orenburg

<b>That is finally version of the VK bot, which parses the schedule from the site uc.osu.ru. This project deployed on Yandex Cloud Functions in conjunction with Yandex Cloud Database (AWS boto3.dynamodb) and Yandex Cloud Message Queue. Bot works without the participation of a local computer and failsafe. It means if any error occured during script working, message with that error will be logged & skipped.
For security reasons, the personal data of the developer's config and virtual environment variables, as well as the secret keys of the VK API are hidden.🇺</b>
