import pandas as pd

ratings = pd.read_csv("Files/Ratings_cleaned.csv")
books = pd.read_csv("Files/Books_cleaned.csv")

# САМЫЙ АКТИВНЫЙ ПОЛЬЗОВАТЕЛЬ + ЕГО РЕАЛЬНЫЕ ОЦЕНКИ

user_most = ratings["User-ID"].value_counts().idxmax()
user_most_data = ratings[ratings["User-ID"] == user_most].copy()

user_most_full = user_most_data.merge(
    books[["ISBN", "Book-Title"]],
    on="ISBN",
    how="left"
)

result = user_most_full[[
    "User-ID",
    "ISBN",
    "Book-Title",
    "Book-Rating"
]].sort_values(by="Book-Rating", ascending=False)

result.to_csv("Files/user_most_full.csv", index=False)

print(result)