SELECT c.CustomerID, c.CustomerName,
       SUM(p.Price * od.Quantity) AS TotalSpent
FROM Customers AS c
INNER JOIN Orders AS o ON c.CustomerID = o.CustomerID
INNER JOIN OrderDetails AS od ON o.OrderID = od.OrderID
INNER JOIN Products AS p ON od.ProductID = p.ProductID
WHERE c.Country = 'France'
GROUP BY c.CustomerID, c.CustomerName
ORDER BY TotalSpent DESC, c.CustomerID ASC;
