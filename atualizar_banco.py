import sqlite3

conexao = sqlite3.connect("nutricontrol.db")

cursor = conexao.cursor()

cursor.execute("ALTER TABLE pacientes ADD COLUMN sexo TEXT")
cursor.execute("ALTER TABLE pacientes ADD COLUMN nivel_atividade TEXT")

conexao.commit()
conexao.close()

print("Banco atualizado com sucesso!")