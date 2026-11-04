SELECT TOP 5 p.ProductID, p.ProductName,
       SUM(od.Quantity) AS Quantity
FROM Products AS p
INNER JOIN OrderDetails AS od ON p.ProductID = od.ProductID
INNER JOIN Orders AS o ON od.OrderID = o.OrderID
WHERE o.OrderDate >= '1996-07-01'
  AND o.OrderDate < '1996-08-01'
GROUP BY p.ProductID, p.ProductName
ORDER BY Quantity DESC, p.ProductID ASC;
