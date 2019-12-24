# Django Admin

### Register your models

To register your model on django admin, is recomended to let ParanoidAdmin handle with admin action. Otherwise you may have
some trouble.

ParanoidAdmin also include some aditional methods to look more "paranoid" on admin page, some functions are:
  * Delete: soft delete instance
  * Permanently delete: hard delete
  * Restore: remode deleted_at date
  * Filter: filter all, only deleted, not deleted

On you  ``admin.py`` register you models like the example below:

```py
# admin.py

from paranoid_model.admin import ParanoidAdmin
from .models import MyModel

admin.site.register(MyModel, ParanoidAdmin)
```

This will allow ParanoidAdmin to handle with admin actions.
