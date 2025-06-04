-- הכנס את המשתמש שלך לטבלת users באופן ידני
INSERT INTO users (id, email, role)
VALUES 
  ('0418af5f-3d46-4983-a126-deaedfaf02ad', 'omri99roter@gmail.com', 'admin')
ON CONFLICT (id) DO UPDATE 
SET email = EXCLUDED.email,
    role = EXCLUDED.role;

-- הוסף גם את המשתמשים הקיימים
INSERT INTO users (id, email, role)
VALUES 
  ('efc386eb-5c7f-4983-ba25-0158a492b5e3', 'user@apex.com', 'user'),
  ('c1884271-a539-4dc4-934b-faeb8cd315a2', 'admin@apex.com', 'admin')
ON CONFLICT (id) DO NOTHING; 