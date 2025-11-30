"""
Mindmap Builder Module
Creates hierarchical topic structure from text
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MindmapBuilder:
    """Build hierarchical mindmap structure from text"""
    
    def __init__(self):
        pass
    
    def build_mindmap(self, sentences: List[str], 
                     keywords: List[tuple],
                     max_topics: int = 5) -> Dict[str, Any]:
        """
        Build hierarchical mindmap structure
        
        Args:
            sentences: List of sentences
            keywords: List of (keyword, score) tuples
            max_topics: Maximum number of main topics
            
        Returns:
            Mindmap structure as nested dictionary
        """
        if not sentences or len(sentences) < 3:
            return {'topics': []}
        
        # Cluster sentences into topics
        clusters = self._cluster_sentences(sentences, n_clusters=max_topics)
        
        # Build topic hierarchy
        topics = self._build_topics(sentences, clusters, keywords)
        
        # Create tree structure
        mindmap = {
            'title': 'Document Overview',
            'topics': topics,
            'total_topics': len(topics)
        }
        
        logger.info(f"Built mindmap with {len(topics)} main topics")
        
        return mindmap
    
    def _cluster_sentences(self, sentences: List[str], 
                          n_clusters: int) -> np.ndarray:
        """
        Cluster sentences using KMeans
        
        Args:
            sentences: List of sentences
            n_clusters: Number of clusters
            
        Returns:
            Array of cluster labels
        """
        try:
            # Limit clusters to reasonable number
            n_clusters = min(n_clusters, len(sentences) // 2, 8)
            n_clusters = max(n_clusters, 2)
            
            # Vectorize sentences
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            # Cluster
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(tfidf_matrix)
            
            return clusters
        except Exception as e:
            logger.error(f"Clustering error: {str(e)}")
            # Fallback: assign all to one cluster
            return np.zeros(len(sentences), dtype=int)
    
    def _build_topics(self, sentences: List[str], 
                     clusters: np.ndarray,
                     keywords: List[tuple]) -> List[Dict[str, Any]]:
        """
        Build topic structure from clusters
        
        Args:
            sentences: List of sentences
            clusters: Cluster labels for each sentence
            keywords: Global keywords
            
        Returns:
            List of topic dictionaries
        """
        topics = []
        keyword_dict = {kw.lower(): score for kw, score in keywords[:20]}
        
        for cluster_id in range(clusters.max() + 1):
            # Get sentences in this cluster
            cluster_sentences = [sentences[i] for i in range(len(sentences)) 
                               if clusters[i] == cluster_id]
            
            if not cluster_sentences:
                continue
            
            # Extract topic name from keywords in cluster
            topic_name = self._extract_topic_name(cluster_sentences, keyword_dict)
            
            # Get subtopics (key sentences)
            subtopics = self._extract_subtopics(cluster_sentences)
            
            topics.append({
                'name': topic_name,
                'subtopics': subtopics,
                'sentence_count': len(cluster_sentences)
            })
        
        return topics
    
    def _extract_topic_name(self, sentences: List[str], 
                           keyword_dict: Dict[str, float]) -> str:
        """
        Extract a name for the topic from its sentences
        
        Args:
            sentences: Sentences in the cluster
            keyword_dict: Dictionary of keywords and scores
            
        Returns:
            Topic name string
        """
        # Combine all sentences
        combined_text = ' '.join(sentences).lower()
        
        # Find most relevant keywords
        topic_keywords = []
        for keyword, score in sorted(keyword_dict.items(), 
                                    key=lambda x: x[1], 
                                    reverse=True):
            if keyword in combined_text:
                topic_keywords.append(keyword.title())
                if len(topic_keywords) >= 3:
                    break
        
        if topic_keywords:
            return ' | '.join(topic_keywords)
        else:
            # Fallback: use first few words of first sentence
            first_words = ' '.join(sentences[0].split()[:4])
            return first_words + '...'
    
    def _extract_subtopics(self, sentences: List[str], 
                          max_subtopics: int = 4) -> List[str]:
        """
        Extract subtopics (key sentences) from cluster
        
        Args:
            sentences: Sentences in cluster
            max_subtopics: Maximum number of subtopics
            
        Returns:
            List of subtopic sentences
        """
        # Limit number of subtopics
        num_subtopics = min(max_subtopics, len(sentences))
        
        if num_subtopics <= 2:
            return sentences[:num_subtopics]
        
        try:
            # Use TF-IDF to find most representative sentences
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            # Calculate average TF-IDF score for each sentence
            scores = np.asarray(tfidf_matrix.mean(axis=1)).flatten()
            
            # Get top sentences
            top_indices = scores.argsort()[-num_subtopics:][::-1]
            top_indices = sorted(top_indices)  # Keep original order
            
            return [sentences[i] for i in top_indices]
        except:
            # Fallback: return first N sentences
            return sentences[:num_subtopics]
    
    def format_as_tree(self, mindmap: Dict[str, Any], 
                      indent: str = "   ") -> str:
        """
        Format mindmap as text tree structure
        
        Args:
            mindmap: Mindmap dictionary
            indent: Indentation string
            
        Returns:
            Formatted tree string
        """
        lines = []
        lines.append(f"📚 {mindmap['title']}")
        lines.append("")
        
        for i, topic in enumerate(mindmap['topics'], 1):
            lines.append(f"{i}. {topic['name']}")
            
            for j, subtopic in enumerate(topic['subtopics'], 1):
                # Shorten subtopic if too long
                subtopic_text = subtopic if len(subtopic) < 80 else subtopic[:77] + "..."
                lines.append(f"{indent}├── {subtopic_text}")
            
            lines.append("")
        
        return '\n'.join(lines)
    
    def format_as_markdown(self, mindmap: Dict[str, Any]) -> str:
        """
        Format mindmap as markdown
        
        Args:
            mindmap: Mindmap dictionary
            
        Returns:
            Markdown formatted string
        """
        lines = []
        lines.append(f"# {mindmap['title']}\n")
        
        for i, topic in enumerate(mindmap['topics'], 1):
            lines.append(f"## {i}. {topic['name']}\n")
            
            for subtopic in topic['subtopics']:
                lines.append(f"- {subtopic}")
            
            lines.append("")
        
        return '\n'.join(lines)
    
    def build_simple_hierarchy(self, sentences: List[str],
                              keywords: List[tuple]) -> Dict[str, Any]:
        """
        Build simple 2-level hierarchy without clustering
        
        Args:
            sentences: List of sentences
            keywords: List of keywords
            
        Returns:
            Simple hierarchy structure
        """
        # Group by top keywords
        keyword_groups = {}
        top_keywords = [kw for kw, score in keywords[:8]]
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            assigned = False
            
            for keyword in top_keywords:
                if keyword.lower() in sentence_lower:
                    if keyword not in keyword_groups:
                        keyword_groups[keyword] = []
                    keyword_groups[keyword].append(sentence)
                    assigned = True
                    break
            
            if not assigned:
                if 'Other Topics' not in keyword_groups:
                    keyword_groups['Other Topics'] = []
                keyword_groups['Other Topics'].append(sentence)
        
        # Build structure
        topics = []
        for keyword, sents in keyword_groups.items():
            if sents:
                topics.append({
                    'name': keyword.title(),
                    'subtopics': sents[:5],  # Limit subtopics
                    'sentence_count': len(sents)
                })
        
        return {
            'title': 'Document Structure',
            'topics': topics,
            'total_topics': len(topics)
        }


if __name__ == "__main__":
    # Test the mindmap builder
    builder = MindmapBuilder()
    sample_sentences = [
        "Machine learning is a subset of AI.",
        "Neural networks process information like the brain.",
        "Deep learning uses multiple layers.",
        "Natural language processing handles text.",
        "NLP includes tasks like translation.",
        "Transformers are state-of-the-art models."
    ]
    sample_keywords = [("machine learning", 0.9), ("neural networks", 0.8), ("nlp", 0.7)]
    
    mindmap = builder.build_mindmap(sample_sentences, sample_keywords, max_topics=2)
    print(builder.format_as_tree(mindmap))
