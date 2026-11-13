
import database


class Client:
    """Represent a community health client."""

    def __init__(self, name, age, sex, residence, client_id=None):
        self.id = client_id
        self.name = name
        self.age = age
        self.sex = sex
        self.residence = residence

    def register(self):
        """Save a new client in the database."""
        self.id = database.add_client(
            self.name,
            self.age,
            self.sex,
            self.residence
        )
        return self.id

    def update(self):
        """Update an existing client's details."""
        if self.id is None:
            return False

        return database.update_client(
            self.id,
            self.name,
            self.age,
            self.sex,
            self.residence
        )

    def delete(self):
        """Delete this client's record."""
        if self.id is None:
            return False

        return database.delete_client(self.id)

    def record_visit(self, visit_date, activity):
        """Record a visit for this client."""
        if self.id is None:
            return False

        return database.record_visit(
            self.id,
            visit_date,
            activity
        )

    def schedule_followup(self, followup_date):
        """Schedule a follow-up for this client."""
        if self.id is None:
            return False

        return database.schedule_followup(
            self.id,
            followup_date
        )

    def complete_followup(self):
        """Mark this client's follow-up as completed."""
        if self.id is None:
            return False

        return database.complete_followup(self.id)
