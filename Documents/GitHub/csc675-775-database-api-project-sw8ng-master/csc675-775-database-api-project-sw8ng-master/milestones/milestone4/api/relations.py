# relationships.py
#
# This file will implement the base code to create relationships between tables.
# For example, getting all the incident reports from a specific user, or getting
# the user who submitted a given incident report.
#
# Note: we will implement this file in class in the ORM demo lecture.
#


class Relation:
    """
        incident = Incident_Report.get(id=7)
        user = incident.user  # returns the User instance linked by user_id
    """
    def __init__(self, model_name, foreign_key, backreference=None, lazy=True):
        """
        :param model_name: Name of the related model class, e.g., 'User'
        :param foreign_key: Name of the column in the current model that holds the foreign key, e.g., 'user_id'
        """
        self.model_name = model_name
        self.fk = foreign_key
        self.backreference = backreference
        self.lazy = lazy
        self.attribute_name = None

    def __set_name__(self, owner, name):
        """
        :param owner: The model class that contains this relation (e.g., Incident_Report)
        :param name: The attribute name used in the model (e.g., 'user')
        """
        self.attribute_name = name

    def __get__(self, instance, owner):
        """
        Called when accessing the relation attribute on a model instance.
        Returns the related object (e.g., User) instead of the Relation descriptor.
        """
        if instance is None:   # class-level access
            return self

        # Check cache for lazy loading
        cache = None
        if self.lazy:
            cache = Cache(self.attribute_name)
            if cache.has_model(instance):
                return cache.get_model(instance)

        # Resolve the target model class from its name (e.g., 'User' -> User)
        target_model = owner.resolve_model(self.model_name)
        # Get the foreign key value from the current instance (e.g., incident.user_id)
        fk_value = getattr(instance, self.fk)

        if target_model is None or fk_value is None:
            return None

        # Fetch the related object using the target model's get() method
        related_obj = target_model.get(id=fk_value)

        # Store in cache for future access
        if self.lazy and cache is not None:
            cache.add_model(instance, related_obj)

        # Set backreference on the related object if required
        if self.backreference:
            setattr(related_obj, self.backreference, instance)

        return related_obj


class Cache:
    """
    Simple internal cache to store a loaded related object on the source instance.
    The cached object is stored under a private attribute name.
    """
    def __init__(self, attribute_name):
        self.cache_name = f"_{attribute_name}_cache"

    def add_model(self, instance, obj):
        setattr(instance, self.cache_name, obj)

    def get_model(self, instance):
        return getattr(instance, self.cache_name)

    def has_model(self, instance):
        return hasattr(instance, self.cache_name)
