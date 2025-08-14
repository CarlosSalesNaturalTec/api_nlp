import sys
import os

# Adiciona o diretório raiz do projeto ao path para permitir importações diretas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
import traceback

def migrate_articles():
    """
    Adiciona o campo 'status: "pending"' a todos os artigos na coleção
    'scraped_articles' que ainda não o possuem.
    """
    print("Iniciando migração de dados...")
    db = get_db()
    articles_ref = db.collection('scraped_articles')
    
    updated_count = 0
    checked_count = 0
    
    try:
        # Usamos .stream() para percorrer todos os documentos da coleção
        articles_snapshot = articles_ref.stream()
        
        # Usamos um batch para realizar as atualizações em lote, o que é mais eficiente
        batch = db.batch()
        
        for doc in articles_snapshot:
            checked_count += 1
            article_data = doc.to_dict()
            
            # Verifica se o campo 'status' já existe no documento
            if 'status' not in article_data:
                print(f"Atualizando documento ID: {doc.id}...")
                doc_ref = articles_ref.document(doc.id)
                batch.update(doc_ref, {'status': 'pending'})
                updated_count += 1
                
                # O Firestore recomenda que um batch não exceda 500 operações.
                # Se tivermos muitos documentos, fazemos o commit em lotes.
                if updated_count % 499 == 0:
                    print("Realizando commit do lote...")
                    batch.commit()
                    # Inicia um novo batch
                    batch = db.batch()

        # Faz o commit final para quaisquer operações restantes no batch
        if updated_count > 0:
            print("Realizando commit final...")
            batch.commit()
            print("\nMigração concluída com sucesso!")
            print(f"{checked_count} documentos verificados.")
            print(f"{updated_count} documentos atualizados.")
        else:
            print("\nNenhum documento precisou ser atualizado. Todos já possuem o campo 'status'.")

    except Exception as e:
        print(f"\nOcorreu um erro durante a migração: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    migrate_articles()
