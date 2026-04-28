import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import async_session, engine
from app.models.user import User, UserRole
from app.models.thematic import Thematic, AccessLevel
from app.models.source import Partition, Folder, Source, SourceStatus
from app.models.document import Document
from app.models.alert import Alert, AlertType, AlertPriority
from app.models.article import Article, ArticleStatus
from app.models.signal import Signal, SignalType
from app.core.security import hash_password

async def seed_data():
    print("Beginning database seed...")
    async with async_session() as db:
        
        # 1. Users
        print("Creating users...")
        admin = User(
            email="admin@veilleai.com",
            password_hash=hash_password("admin123"),
            full_name="Admin Principal",
            role=UserRole.ADMIN
        )
        analyst = User(
            email="analyst@veilleai.com",
            password_hash=hash_password("analyst456"),
            full_name="Veilleur Expert",
            role=UserRole.ANALYST
        )
        db.add_all([admin, analyst])
        await db.flush()

        # 2. Thematics
        print("Creating thematics...")
        ai_thematic = Thematic(
            name="Intelligence Artificielle",
            color="#ec4899",
            description="Veille sur les avancées de l'IA générative et de l'Agentic AI",
            access_portal=AccessLevel.PUBLIC,
            access_admin=AccessLevel.PUBLIC,
            created_by=admin.id
        )
        cyber_thematic = Thematic(
            name="Cybersécurité",
            color="#3b82f6",
            description="Nouvelles menaces et solutions de sécurité",
            access_portal=AccessLevel.PUBLIC,
            access_admin=AccessLevel.PRIVATE,
            created_by=admin.id
        )
        db.add_all([ai_thematic, cyber_thematic])
        await db.flush()

        # 3. Sources Hierarchy
        print("Creating sources...")
        ai_partition = Partition(thematic_id=ai_thematic.id, name="Presse Tech", order_index=1)
        db.add(ai_partition)
        await db.flush()
        
        ai_folder = Folder(partition_id=ai_partition.id, name="Recherche", order_index=1)
        db.add(ai_folder)
        await db.flush()

        ai_source1 = Source(
            folder_id=ai_folder.id,
            name="Arxiv AI",
            url="https://arxiv.org/list/cs.AI/recent",
            type="rss",
            status=SourceStatus.ACTIVE,
            last_crawled_at=datetime.utcnow() - timedelta(hours=2)
        )
        ai_source2 = Source(
            folder_id=ai_folder.id,
            name="TechCrunch AI",
            url="https://techcrunch.com/category/artificial-intelligence/",
            type="web",
            status=SourceStatus.ACTIVE,
            last_crawled_at=datetime.utcnow() - timedelta(minutes=30)
        )
        db.add_all([ai_source1, ai_source2])
        await db.flush()

        # 4. Documents & Alerts
        print("Creating documents and alerts...")
        doc1 = Document(
            source_id=ai_source1.id,
            url="https://arxiv.org/abs/example",
            title="Introduction to Agentic AI Systems",
            content="Agentic AI systems represent the next evolution in artificial intelligence, moving beyond simple conversational interfaces to systems capable of autonomous planning and tool execution.",
            summary="New research on Agentic AI capabilities for autonomous task execution.",
            language="en",
            tags=["Agentic AI", "Research", "Autonomous"],
            sentiment_score=0.8,
            collected_at=datetime.utcnow() - timedelta(hours=5)
        )
        db.add(doc1)
        await db.flush()

        alert1 = Alert(
            document_id=doc1.id,
            thematic_id=ai_thematic.id,
            type=AlertType.NEW_DOCUMENT,
            priority=AlertPriority.HIGH,
            ai_score=0.92,
            is_read=False,
            created_at=datetime.utcnow() - timedelta(hours=5)
        )
        db.add(alert1)
        
        doc2 = Document(
            source_id=ai_source2.id,
            url="https://techcrunch.com/example",
            title="OpenAI releases new reasoning model",
            content="OpenAI has announced a new iteration of their language model, heavily focused on methodical reasoning and multi-step problem solving.",
            summary="OpenAI launches step-by-step reasoning LLM.",
            language="en",
            tags=["OpenAI", "LLM", "Reasoning"],
            sentiment_score=0.6,
            collected_at=datetime.utcnow() - timedelta(minutes=25)
        )
        db.add(doc2)
        await db.flush()

        alert2 = Alert(
            document_id=doc2.id,
            thematic_id=ai_thematic.id,
            type=AlertType.KEYWORD_MATCH,
            priority=AlertPriority.CRITICAL,
            ai_score=0.98,
            is_read=True,
            created_at=datetime.utcnow() - timedelta(minutes=25)
        )
        db.add(alert2)
        await db.flush()

        # 5. Articles
        print("Creating articles...")
        article1 = Article(
            thematic_id=ai_thematic.id,
            alert_id=alert2.id,
            title="L'évolution du raisonnement dans les LLMs",
            content="Avec la sortie des nouveaux modèles, nous observons un changement de paradigme. Les modèles ne se contentent plus de prédire le prochain token, ils planifient leurs réponses.",
            summary="Analyse de la dernière annonce concernant les capacités de raisonnement des LLMs.",
            status=ArticleStatus.PUBLISHED,
            language="fr",
            author_id=analyst.id,
            tags=["LLM", "OpenAI", "Analyse"],
            published_at=datetime.utcnow() - timedelta(minutes=5)
        )
        db.add(article1)

        # 6. Signals
        print("Creating signals...")
        signal1 = Signal(
            thematic_id=ai_thematic.id,
            type=SignalType.TREND,
            description="Forte augmentation du volume d'articles concernant les 'Agents Autonomes' dans les flux de recherche.",
            confidence=0.88,
            trend_data={
                "keywords": ["Agents", "Autonomous", "Planning"],
                "series": [
                    {"date": "10/04", "count": 5}, {"date": "11/04", "count": 12}, 
                    {"date": "12/04", "count": 28}, {"date": "13/04", "count": 65}
                ]
            }
        )
        db.add(signal1)

        await db.commit()
        print("Seed data successfully inserted!")

if __name__ == "__main__":
    asyncio.run(seed_data())
