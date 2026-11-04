SELECT c.CustomerID, c.CustomerName, o.OrderDate,
       od.Quantity AS Quantity
FROM Customers AS c
INNER JOIN Orders AS o ON c.CustomerID = o.CustomerID
INNER JOIN OrderDetails AS od ON o.OrderID = od.OrderID
INNER JOIN Products AS p ON od.ProductID = p.ProductID
WHERE p.ProductName = 'Tofu'
ORDER BY c.CustomerID ASC, o.OrderDate ASC, o.OrderID ASC;
