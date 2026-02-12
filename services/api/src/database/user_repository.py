"""Repository for user CRUD operations."""
from sqlmodel import Session, select

from services.api.src.database.db_models import UserTable


class UserRepository:
    """Repository for user database operations.

    Attributes:
        session: SQLModel database session
    """

    def __init__(self, session: Session):
        self.session = session

    def get_by_google_id(self, google_id: str) -> UserTable | None:
        """Find a user by their Google subject ID.

        Args:
            google_id: Google OAuth subject identifier

        Returns:
            User if found, None otherwise.
        """
        statement = select(UserTable).where(UserTable.google_id == google_id)
        return self.session.exec(statement).first()

    def get_by_id(self, user_id: int) -> UserTable | None:
        """Find a user by primary key.

        Args:
            user_id: User's database ID

        Returns:
            User if found, None otherwise.
        """
        return self.session.get(UserTable, user_id)

    def create(
        self,
        google_id: str,
        email: str,
        name: str,
        picture_url: str | None = None,
    ) -> UserTable:
        """Create a new user.

        Args:
            google_id: Google OAuth subject identifier
            email: User email
            name: User display name
            picture_url: Profile picture URL

        Returns:
            The newly created user.
        """
        user = UserTable(
            google_id=google_id,
            email=email,
            name=name,
            picture_url=picture_url,
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def find_or_create(
        self,
        google_id: str,
        email: str,
        name: str,
        picture_url: str | None = None,
    ) -> tuple[UserTable, bool]:
        """Find an existing user by Google ID, or create a new one.

        Args:
            google_id: Google OAuth subject identifier
            email: User email
            name: User display name
            picture_url: Profile picture URL

        Returns:
            Tuple of (user, is_new) where is_new is True if the user was just created.
        """
        existing = self.get_by_google_id(google_id)
        if existing:
            # Update profile info on every login
            self.update_profile(existing, email=email, name=name, picture_url=picture_url)
            return existing, False

        new_user = self.create(
            google_id=google_id,
            email=email,
            name=name,
            picture_url=picture_url,
        )
        return new_user, True

    def update_profile(
        self,
        user: UserTable,
        email: str | None = None,
        name: str | None = None,
        picture_url: str | None = None,
    ) -> UserTable:
        """Update a user's profile fields.

        Args:
            user: User to update
            email: New email (if changed)
            name: New display name (if changed)
            picture_url: New picture URL (if changed)

        Returns:
            The updated user.
        """
        if email is not None:
            user.email = email
        if name is not None:
            user.name = name
        if picture_url is not None:
            user.picture_url = picture_url
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
