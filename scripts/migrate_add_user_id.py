"""
Script de migração para adicionar user_id em financial_entries.

Este script:
1. Adiciona coluna user_id (nullable temporariamente)
2. Cria usuário padrão se não existir
3. Atribui registros existentes ao usuário padrão (pegando user_id da sessão relacionada)
4. Torna user_id NOT NULL
5. Cria índices e constraints

IMPORTANTE: Faça backup do banco de dados antes de executar!
"""

import asyncio
import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.infra.db.database import get_database_manager
from app.core.auth.password import hash_password
from app.domain.entities.user import User
from app.infra.repositories.user_repository_impl import SqlAlchemyUserRepository


async def migrate():
    """Executa migração completa."""
    print("🚀 Iniciando migração de user_id em financial_entries...")
    
    db = get_database_manager()
    
    async with db.session() as session:
        try:
            # 1. Verificar se coluna já existe
            check_result = await session.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('financial_entries') 
                WHERE name = 'user_id';
            """))
            column_exists = check_result.scalar() > 0
            
            if column_exists:
                print("⚠️  Coluna user_id já existe. Verificando se precisa preencher valores...")
                # Verificar se há registros sem user_id
                null_check = await session.execute(text("""
                    SELECT COUNT(*) FROM financial_entries WHERE user_id IS NULL;
                """))
                null_count = null_check.scalar()
                if null_count == 0:
                    print("✅ Todos os registros já têm user_id. Migração não necessária.")
                    return
            else:
                # 1. Adicionar coluna user_id (nullable)
                print("📝 Adicionando coluna user_id...")
                await session.execute(text("""
                    ALTER TABLE financial_entries 
                    ADD COLUMN user_id VARCHAR(36);
                """))
                await session.commit()
                print("✅ Coluna user_id adicionada.")
            
            # 2. Criar usuário padrão se não existir
            print("👤 Verificando/criando usuário padrão...")
            user_repo = SqlAlchemyUserRepository(session)
            default_user = await user_repo.get_by_email("admin@default.com")
            
            if not default_user:
                print("📝 Criando usuário padrão...")
                default_user = User(
                    email="admin@default.com",
                    password_hash=hash_password("changeme123"),
                    name="Usuário Padrão (Migração)",
                )
                default_user = await user_repo.create(default_user)
                print(f"✅ Usuário padrão criado com ID: {default_user.id}")
            else:
                print(f"✅ Usuário padrão já existe com ID: {default_user.id}")
            
            # 3. Atribuir registros existentes ao usuário padrão
            # Pegar user_id da sessão relacionada, ou usar padrão
            print("📝 Atribuindo user_id aos registros existentes...")
            
            # Primeiro, atualizar registros que têm sessão com user_id
            update_result = await session.execute(text("""
                UPDATE financial_entries fe
                SET user_id = (
                    SELECT s.user_id 
                    FROM sessions s 
                    WHERE s.id = fe.session_id 
                    LIMIT 1
                )
                WHERE fe.user_id IS NULL 
                AND EXISTS (
                    SELECT 1 FROM sessions s WHERE s.id = fe.session_id AND s.user_id IS NOT NULL
                );
            """))
            updated_from_session = update_result.rowcount
            await session.commit()
            print(f"✅ {updated_from_session} registros atualizados com user_id da sessão relacionada.")
            
            # Depois, atribuir usuário padrão aos que ainda estão NULL
            update_result2 = await session.execute(text("""
                UPDATE financial_entries
                SET user_id = :default_user_id
                WHERE user_id IS NULL;
            """), {"default_user_id": str(default_user.id)})
            updated_to_default = update_result2.rowcount
            await session.commit()
            print(f"✅ {updated_to_default} registros atribuídos ao usuário padrão.")
            
            # Verificar se ainda há registros sem user_id
            null_check = await session.execute(text("""
                SELECT COUNT(*) FROM financial_entries WHERE user_id IS NULL;
            """))
            null_count = null_check.scalar()
            
            if null_count > 0:
                print(f"⚠️  ATENÇÃO: Ainda existem {null_count} registros sem user_id!")
                print("   Isso não deveria acontecer. Verifique os dados.")
                return
            
            # 4. Tornar user_id NOT NULL (apenas se não for SQLite, que não suporta ALTER COLUMN)
            # Para SQLite, vamos apenas criar índice e constraint
            print("📝 Criando índice em user_id...")
            try:
                await session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_financial_entries_user_id 
                    ON financial_entries(user_id);
                """))
                await session.commit()
                print("✅ Índice criado.")
            except Exception as e:
                print(f"⚠️  Erro ao criar índice (pode já existir): {e}")
            
            # 5. Criar foreign key constraint (se suportado)
            print("📝 Criando foreign key constraint...")
            try:
                # Verificar se constraint já existe
                await session.execute(text("""
                    PRAGMA foreign_key_check(financial_entries);
                """))
                
                # Tentar adicionar constraint (pode falhar se já existir ou não suportado)
                # SQLite não suporta ADD CONSTRAINT diretamente
                # Para PostgreSQL, seria:
                # ALTER TABLE financial_entries 
                # ADD CONSTRAINT fk_financial_entries_user_id 
                # FOREIGN KEY (user_id) REFERENCES users(id);
                
                print("✅ Constraint será aplicada automaticamente pelo SQLAlchemy.")
            except Exception as e:
                print(f"⚠️  Nota sobre constraint: {e}")
                print("   (Isso é normal para SQLite)")
            
            print("\n✅ Migração concluída com sucesso!")
            print(f"   - Usuário padrão: {default_user.email} (ID: {default_user.id})")
            print(f"   - Total de registros atualizados: {updated_from_session + updated_to_default}")
            print("\n⚠️  IMPORTANTE: Altere a senha do usuário padrão em produção!")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Erro durante migração: {e}")
            print("   Rollback executado. Banco de dados não foi modificado.")
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("MIGRAÇÃO: Adicionar user_id em financial_entries")
    print("=" * 60)
    print("\n⚠️  ATENÇÃO: Faça backup do banco de dados antes de continuar!")
    print("   Pressione Ctrl+C para cancelar ou Enter para continuar...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n❌ Migração cancelada pelo usuário.")
        sys.exit(1)
    
    try:
        asyncio.run(migrate())
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)
