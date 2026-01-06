/*Prix moyen des livres par catégorie*/
SELECT
    c.name AS category,
    COUNT(b.id) AS nb_books,
    ROUND(AVG(b.price), 2) AS avg_price
FROM books b
JOIN category c ON b.category_id = c.id
GROUP BY c.name
ORDER BY avg_price DESC;

/*Livre par catégorie*/
SELECT
    b.title,
    b.price,
    b.rating,
    b.stock,
    c.name AS category
FROM books b
JOIN category c ON b.category_id = c.id
ORDER BY c.name, b.title;

/* Top 5 des livres les plus chers */
SELECT
    title,
    price,
    rating
FROM books
ORDER BY price DESC
LIMIT 5;

/* Top 3 par catégorie : */
SELECT *
FROM (
    SELECT
        c.name AS category,
        b.title,
        b.price,
        ROW_NUMBER() OVER (
            PARTITION BY c.name
            ORDER BY b.price DESC
        ) AS rn
    FROM books b
    JOIN category c ON b.category_id = c.id
) ranked
WHERE rn <= 3;


