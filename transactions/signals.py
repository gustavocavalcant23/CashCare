# accounts/signals.py
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from transactions.models import Transaction


User = get_user_model()


@receiver(pre_save, sender=Transaction)
def capture_old_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Transaction.objects.get(pk=instance.pk)
            instance._old_signed_amount = old.signed_amount
            instance._old_is_completed = old.is_completed
            print(f"PRE-SAVE: Old value = {instance._old_signed_amount}, Old completed = {instance._old_is_completed}")
        except Transaction.DoesNotExist:
            pass


@receiver(post_save, sender=Transaction)
def update_balance_on_save(sender, instance, created, **kwargs):
    user = instance.user

    if created:
        if instance.is_completed:
            user.balance += instance.signed_amount

    else:
        if hasattr(instance, '_old_signed_amount') and hasattr(instance, '_old_is_completed'):
            old_value = instance._old_signed_amount
            old_completed = instance._old_is_completed
            new_value = instance.signed_amount
            new_completed = instance.is_completed

            if not old_completed and new_completed:
                user.balance += new_value

            elif old_completed and not new_completed:
                user.balance -= old_value

            elif old_completed and new_completed and old_value != new_value:
                user.balance -= old_value
                user.balance += new_value

        else:
            user.balance = sum(
                t.signed_amount
                for t in user.transactions.filter(is_completed=True)
            )

    user.save()


@receiver(post_delete, sender=Transaction)
def update_balance_on_delete(sender, instance, **kwargs):
    user = instance.user
    if instance.is_completed:
        user.balance -= instance.signed_amount
        user.save()
