from datetime import date, datetime
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Table, Text, UniqueConstraint, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

Engine = create_engine("sqlite:///RecipenMealPlanner.db", echo=True)

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(25))


# PARENT MODEL FOR INSTRUCTION AND THE INGREDIENTS

# ----------- Junction Table ------
# recipe_tags = Table(
#     "recipe_tags",
#     Base.metadata,
#     Column("recipe_id", Integer, ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True),
#     Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
#     )

class Recipe(Base):
    __tablename__ = "Recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True) #OPTIONAL
    cuisine: Mapped[str] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(50))
    prep_time: Mapped[int] = mapped_column(Integer)
    cook_time: Mapped[int] = mapped_column(Integer)
    servings: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[str] = mapped_column(String(20))
    image_path: Mapped[str] = mapped_column(Text, nullable=True) #OPTIONAL
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=func.now(), server_default=func.now())

    #  ---------- ONE TO MANY RELATION ---------
    # Lookup for ingredients
    # It doesn't create a new column, it lets the table interact with the each other as object models
    # e.g. if a new ingredient is added to the Ingredient table, it will automatically assing it with the recipe's ID
    ingredients: Mapped[list["Ingredient"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")
    
    # Lookup for instructions (steps)
    instructions: Mapped[list["Instruction"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")

    # ---------- MANY TO MANY RELATIONSHIO ---------
    tags: Mapped[list["Tag"]] = relationship(secondary="recipe_tags", back_populates="recipe")


class Tag(Base):
    __tablename__ = "Tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(70), unique=True, nullable=False)

    recipe: Mapped[list["Recipe"]] = relationship(secondary="recipe_tags", back_populates="tags")

# ----------- Junction Table ------
recipe_tags = Table(
    "recipe_tags",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("Recipes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("Tags.id", ondelete="CASCADE"), primary_key=True),
    )

class Ingredient(Base):
    __tablename__ = "Ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("Recipes.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(50))
    # To estabish the interaction with the Recipe table
    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")

class Instruction(Base):
    __tablename__ = "Instructions"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("Recipes.id"), nullable=False)
    stepNumber: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text)

    # To estabish the interaction with the Recipe table
    # Many-to-one relationship back to Recipe
    recipe: Mapped["Recipe"] = relationship(back_populates="instructions")

class Favorite(Base):
    __tablename__ = "Favorites"

    fav_id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("Recipes.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id", ondelete="CASCADE"), nullable=False)

#     # Ensures a user can't favorite the exact same recipe twice
#     # it tells the db to enforce the rule that: a combination of recipe_id+user_id is always unique
    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe"),
    )
#     # Optional: Relationships for easy querying
#     # they are object-oriented bridges created by SQLAlchemy. They link your Favorite model directly 
#     # to your Recipe and User models.
#     # when requied, instead of writing JOIN queries you can get the name, title, descript etc of the recipe with 
#     # just the fav id as; fav.recipe.title etc
    recipe = relationship("Recipe")
    user = relationship("Users")

class MealPlan(Base):
    __tablename__ = "Meals"

    id: Mapped[int] = mapped_column(primary_key=True)
    week_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    meal_slot: Mapped[str] = mapped_column(String(10))
    recipe_id: Mapped[int] = mapped_column(ForeignKey("Recipes.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column (ForeignKey("Users.id", ondelete="CASCADE"), nullable=False)

    recipe = relationship("Recipe")
    user = relationship("Users")



# creating the database tables
Base.metadata.create_all(Engine)

with Session(Engine) as session:

    read_users = session.query(Users).all()
    for user in read_users:
        print(user)