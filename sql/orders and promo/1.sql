SELECT 
    table2.promocode, 
    SUM(table1.requested_amount + table1.approved_amount) AS total_amount 
FROM 
    table2 
JOIN 
    table1  
ON 
    table1.id = CAST(SUBSTRING(table2.special_marks, '{"request id": "(.*?)"}') AS text) 
GROUP BY 
    table2.promocode
ORDER BY 
    total_amount DESC;