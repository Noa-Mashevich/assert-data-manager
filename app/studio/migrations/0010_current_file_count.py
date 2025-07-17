from django.db import migrations

from studio.models.file_status import FileStatus


def populate_current_file_count(apps, schema_editor):
    ElementData = apps.get_model('studio', 'ElementData')
    RoomData = apps.get_model('studio', 'RoomData')
    FileOwnership = apps.get_model('studio', 'FileOwnership')
    FileNotification = apps.get_model('studio', 'FileNotification')

    for element_data in ElementData.objects.all():
        file_ready_count = 0

        file_ownerships = FileOwnership.objects.filter(element_data=element_data)
        for file_ownership in file_ownerships:
            file_notifications = FileNotification.objects.filter(file_id=file_ownership.file_id, status=FileStatus.Ready)
            if file_notifications.exists():
                file_ready_count += 1

        element_data.current_file_count = file_ready_count

        element_data.save()

    for room_data in RoomData.objects.all():
        file_ready_count = 0

        file_ownerships = FileOwnership.objects.filter(room_data=room_data)
        for file_ownership in file_ownerships:
            file_notifications = FileNotification.objects.filter(file_id=file_ownership.file_id, status=FileStatus.Ready)
            if file_notifications.exists():
                file_ready_count += 1

        room_data.current_file_count = file_ready_count

        room_data.save()


class Migration(migrations.Migration):

    dependencies = [
        ('studio', '0009_elementdata_current_file_count_and_more'),
    ]

    operations = [
        migrations.RunPython(code=populate_current_file_count, reverse_code=migrations.RunPython.noop),
    ]
