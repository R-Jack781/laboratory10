# bug_app/models.py
from django.db import models

class Programmer(models.Model):
    surname = models.CharField(max_length=50, verbose_name="Прізвище")
    first_name = models.CharField(max_length=50, verbose_name="Ім'я")
    phone = models.CharField(max_length=15, unique=True, verbose_name="Телефон")

    class Meta:
        db_table = 'programmers'
        verbose_name = "Програміст"
        verbose_name_plural = "Програмісти"
    
    def __str__(self):
        return f"{self.surname} {self.first_name}"

class Error(models.Model):
    LEVEL_CHOICES = [
        ('critical', 'Критична'), ('important', 'Важлива'), ('minor', 'Незначна')
    ]
    CATEGORY_CHOICES = [
        ('interface', 'Інтерфейс'), ('data', 'Дані'), ('algorithm', 'Розрахунковий алгоритм'),
        ('other', 'Інше'), ('unknown category', 'Невідома категорія')
    ]
    SOURCE_CHOICES = [
        ('user', 'Користувач'), ('tester', 'Тестувальник')
    ]

    error_description = models.TextField(verbose_name="Опис помилки")
    date_received = models.DateField(verbose_name="Дата надходження")
    error_level = models.CharField(max_length=10, choices=LEVEL_CHOICES, verbose_name="Рівень помилки")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Категорія")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, verbose_name="Джерело")

    class Meta:
        db_table = 'errors'
        verbose_name = "Помилка"
        verbose_name_plural = "Помилки"

    def __str__(self):
        return f"Помилка #{self.pk} ({self.error_level})"

class BugFix(models.Model):
    DURATION_CHOICES = [
        (1, '1 день'), (2, '2 дні'), (3, '3 дні')
    ]

    error = models.ForeignKey(Error, on_delete=models.CASCADE, verbose_name="Помилка")
    programmer = models.ForeignKey(Programmer, on_delete=models.RESTRICT, verbose_name="Програміст")
    start_date = models.DateField(verbose_name="Дата початку виправлення")
    duration_days = models.IntegerField(choices=DURATION_CHOICES, verbose_name="Термін виправлення (днів)")
    cost_per_day = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Вартість 1 дня роботи")

    @property
    def total_cost(self):
        return self.duration_days * self.cost_per_day

    class Meta:
        db_table = 'bug_fixes'
        verbose_name = "Виправлення помилки"
        verbose_name_plural = "Виправлення помилок"

    def __str__(self):
        return f"Виправлення для помилки #{self.error.pk}"