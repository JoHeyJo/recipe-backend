# recipe-backend
Repo layer returns instances & queries

Service layer serialize instances & builds

# Recipe Sharing App

A backend API for managing recipes, recipe books, and sharing between users.

## Tech Stack

- **Framework:** Flask
- **ORM:** SQLAlchemy (modern 2.0 style with type annotations)
- **Database:** PostgreSQL
- **Auth:** JWT

## Data Models

### User
Stores user account information and links to their books.

### Book
Organizational container for recipes. Each book has a `book_type`:
- `standard` — regular user-created book
- `shared_inbox` — system-created book for receiving shared recipes (one per user)

### Recipe
Recipe content (name, notes, ingredients, etc.). Ownership is tracked via `created_by_id`.

### UserBook (Association)
Many-to-many relationship between users and books. Stores `role`:
- `owner` — full control, can share and delete
- `collaborator` — can add/edit recipes
- `viewer` — read-only access

A partial unique index enforces one owner per book.

### RecipeBook (Association)
Many-to-many relationship between recipes and books. A recipe can exist in multiple books.

## Core Features

### Recipe Sharing
Users can share recipes they own with other users.

**Flow:**
1. User A shares a recipe with User B
2. Recipe is added to User B's shared inbox
3. User B sees the recipe as read-only (it's a reference, not a copy)
4. Updates by User A are reflected automatically

**Permissions:**
- Only the recipe owner (`created_by_id`) can share or edit
- Recipients can view but not modify shared recipes

### Copying a Recipe
Recipients can copy a shared recipe to one of their own books.

**Flow:**
1. User B copies a recipe from their shared inbox to a personal book
2. A new recipe is created with `created_by_id = User B`
3. The copy is fully independent — User B can edit freely
4. Original remains in shared inbox (unless manually removed)

### Book Sharing
Users can share entire books with others, granting `collaborator` or `viewer` access.

**Flow:**
1. User A shares a book with User B
2. A new `UserBook` row is created linking User B to the book
3. User B's role determines their permissions

### Removing Shared Recipes
Recipients can remove recipes from their shared inbox.

**Authorization:** Backend verifies the user owns the shared inbox before deletion.

## Authorization Pattern

All mutations verify authorization on the backend. Client-side checks are for UX only.

```python
# Example: sharing a recipe
recipe = db.session.get(Recipe, recipe_id)

if recipe.created_by_id != current_user.id:
    abort(403)
```

For book access:

```python
user_book = db.session.execute(
    select(UserBook).where(
        UserBook.book_id == book_id,
        UserBook.user_id == current_user.id
    )
).scalar_one_or_none()

if not user_book:
    abort(403)
```

## API Response Patterns

### Book Payload
Books are serialized with both intrinsic properties and user-specific relationship data:

```json
{
  "id": 1,
  "title": "Dinner Recipes",
  "description": "Weeknight favorites",
  "book_type": "standard",
  "book_role": "owner"
}
```

- `book_type` comes from `Book`
- `book_role` comes from `UserBook`

### Sharing Response
When sharing a recipe:
- `recipe` — always returned (the shared recipe)
- `book` — only returned if the shared inbox was just created

Client adds the book to state only if present, then adds the recipe to the shared inbox.

## Key Design Decisions

1. **Shared recipes are references, not copies.** No duplication until the recipient explicitly copies.

2. **Ownership is singular.** `Recipe.created_by_id` determines who can edit/share. Copying creates a new owner.

3. **Roles describe capabilities, not book types.** A `viewer` could be viewing a standard book or a shared inbox — the role determines what they can do.

4. **The shared inbox is special.** It's system-created, can't be deleted, and enforces read-only access to its contents.

5. **Backend always verifies authorization.** Client-side guards are UX conveniences, not security boundaries.