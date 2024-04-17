from django.db import models

# Create your models here.
class TelegramUser(models.Model):
    telegram_id = models.CharField(max_length=250)

    def __str__(self):
        return self.telegram_id

class Word(models.Model):
    word = models.CharField(max_length=250)
    definition = models.TextField()
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.word

