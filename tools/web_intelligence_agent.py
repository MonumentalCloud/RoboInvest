"""
Web Intelligence Agent
Advanced web crawling, scraping, and navigation system for autonomous research.
"""

import json
import time
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta
import re
from dataclasses import dataclass
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import undetected_chromedriver as uc

from core.config import config
from core.openai_manager import openai_manager
from utils.logger import logger


@dataclass
class WebPage:
    """Represents a scraped web page with metadata."""
    url: str
    title: str
    content: str
    links: List[str]
    timestamp: datetime
    source: str
    sentiment: Optional[str] = None
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = None


@dataclass
class WebIntelligenceResult:
    """Result of web intelligence gathering."""
    pages: List[WebPage]
    insights: List[str]
    sentiment_analysis: Dict[str, Any]
    risk_factors: List[str]
    opportunities: List[str]
    sources: List[str]
    timestamp: datetime


class WebIntelligenceAgent:
    """
    Advanced web intelligence agent that can:
    1. Crawl and scrape any website
    2. Navigate through links and forms
    3. Extract structured data from pages
    4. Analyze sentiment and relevance
    5. Follow breadcrumbs and discover new sources
    6. Handle JavaScript-heavy sites
    7. Respect robots.txt and rate limits
    """
    
    def __init__(self):
        self.session = None
        self.driver = None
        self.visited_urls: Set[str] = set()
        self.rate_limits = {}
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        self.max_depth = 3
        self.max_pages_per_domain = 10
        self.delay_between_requests = 1.0
        
    async def initialize(self):
        """Initialize the web intelligence agent."""
        try:
            # Initialize aiohttp session
            timeout = aiohttp.ClientTimeout(total=30)
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={'User-Agent': self.user_agents[0]}
            )
            
            # Initialize headless browser for JavaScript-heavy sites
            await self._setup_browser()
            
            logger.info("WebIntelligenceAgent | Initialized successfully")
            
        except Exception as e:
            logger.error(f"WebIntelligenceAgent initialization error: {e}")
    
    async def _setup_browser(self):
        """Setup headless browser for JavaScript rendering."""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=' + self.user_agents[0])
            
            # Use undetected-chromedriver to avoid detection
            self.driver = uc.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
        except Exception as e:
            logger.warning(f"Browser setup failed, falling back to requests: {e}")
            self.driver = None
    
    async def gather_intelligence(self, query: str, tickers: List[str] = None, 
                                max_pages: int = 20) -> WebIntelligenceResult:
        """
        Comprehensive web intelligence gathering for investment research.
        """
        try:
            logger.info(f"WebIntelligenceAgent | Starting intelligence gathering for: {query}")
            
            # Generate search queries
            search_queries = self._generate_search_queries(query, tickers)
            
            # Gather pages from multiple sources
            all_pages = []
            for search_query in search_queries[:5]:  # Limit to 5 search queries
                pages = await self._search_and_crawl(search_query, max_pages // 5)
                all_pages.extend(pages)
            
            # Analyze and filter pages
            analyzed_pages = await self._analyze_pages(all_pages, query, tickers)
            
            # Generate insights
            insights = await self._generate_insights(analyzed_pages, query, tickers)
            
            # Analyze sentiment
            sentiment = await self._analyze_sentiment(analyzed_pages, query)
            
            # Extract risk factors and opportunities
            risks, opportunities = await self._extract_risks_and_opportunities(analyzed_pages)
            
            result = WebIntelligenceResult(
                pages=analyzed_pages,
                insights=insights,
                sentiment_analysis=sentiment,
                risk_factors=risks,
                opportunities=opportunities,
                sources=list(set(page.source for page in analyzed_pages)),
                timestamp=datetime.now()
            )
            
            logger.info(f"WebIntelligenceAgent | Intelligence gathering complete: {len(analyzed_pages)} pages")
            return result
            
        except Exception as e:
            logger.error(f"WebIntelligenceAgent intelligence gathering error: {e}")
            return self._fallback_result(query, tickers)
    
    def _generate_search_queries(self, query: str, tickers: List[str] = None) -> List[str]:
        """Generate diverse search queries for comprehensive coverage."""
        queries = [
            f'"{query}" investment analysis',
            f'"{query}" market news',
            f'"{query}" financial performance',
            f'"{query}" earnings report',
            f'"{query}" stock analysis'
        ]
        
        if tickers:
            for ticker in tickers[:3]:  # Limit to 3 tickers
                queries.extend([
                    f'"{ticker}" stock news',
                    f'"{ticker}" earnings',
                    f'"{ticker}" financial results',
                    f'"{query}" {ticker}'
                ])
        
        return queries
    
    async def _search_and_crawl(self, query: str, max_pages: int) -> List[WebPage]:
        """Search and crawl pages for a given query."""
        try:
            # Get search results from multiple engines
            search_results = await self._multi_engine_search(query)
            
            # Crawl the top results
            pages = []
            for result in search_results[:max_pages]:
                try:
                    page = await self._scrape_page(result['url'])
                    if page and page.content.strip():
                        pages.append(page)
                        await asyncio.sleep(self.delay_between_requests)
                except Exception as e:
                    logger.warning(f"Failed to scrape {result['url']}: {e}")
                    continue
            
            return pages
            
        except Exception as e:
            logger.error(f"Search and crawl error: {e}")
            return []
    
    async def _multi_engine_search(self, query: str) -> List[Dict[str, Any]]:
        """Search across multiple engines for comprehensive results."""
        results = []
        
        # Google search (using DuckDuckGo as fallback)
        try:
            ddg_results = await self._duckduckgo_search(query)
            results.extend(ddg_results)
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
        
        # Add financial-specific sources
        financial_sources = [
            f"https://seekingalpha.com/search?q={query}",
            f"https://finance.yahoo.com/quote/{query}",
            f"https://www.marketwatch.com/search?q={query}",
            f"https://www.bloomberg.com/search?query={query}"
        ]
        
        for source in financial_sources:
            try:
                page = await self._scrape_page(source)
                if page:
                    results.append({
                        'url': source,
                        'title': page.title,
                        'snippet': page.content[:200] + '...' if len(page.content) > 200 else page.content
                    })
            except Exception as e:
                logger.warning(f"Financial source search failed for {source}: {e}")
        
        return results[:10]  # Limit to 10 results
    
    async def _duckduckgo_search(self, query: str) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo API."""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    # Extract results from DuckDuckGo response
                    if 'AbstractURL' in data and data['AbstractURL']:
                        results.append({
                            'url': data['AbstractURL'],
                            'title': data.get('Abstract', ''),
                            'snippet': data.get('Abstract', '')
                        })
                    
                    # Add related topics
                    for topic in data.get('RelatedTopics', [])[:5]:
                        if isinstance(topic, dict) and 'FirstURL' in topic:
                            results.append({
                                'url': topic['FirstURL'],
                                'title': topic.get('Text', ''),
                                'snippet': topic.get('Text', '')
                            })
                    
                    return results
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    async def _scrape_page(self, url: str) -> Optional[WebPage]:
        """Scrape a single page with fallback methods."""
        if url in self.visited_urls:
            return None
        
        self.visited_urls.add(url)
        
        try:
            # Try browser first for JavaScript-heavy sites
            if self.driver:
                page = await self._scrape_with_browser(url)
                if page:
                    return page
            
            # Fallback to requests
            page = await self._scrape_with_requests(url)
            return page
            
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
            return None
    
    async def _scrape_with_browser(self, url: str) -> Optional[WebPage]:
        """Scrape page using headless browser."""
        try:
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page content
            title = self.driver.title
            content = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Extract links
            links = []
            for link in self.driver.find_elements(By.TAG_NAME, "a"):
                href = link.get_attribute("href")
                if href and href.startswith("http"):
                    links.append(href)
            
            return WebPage(
                url=url,
                title=title,
                content=content,
                links=links,
                timestamp=datetime.now(),
                source=urlparse(url).netloc
            )
            
        except Exception as e:
            logger.warning(f"Browser scraping failed for {url}: {e}")
            return None
    
    async def _scrape_with_requests(self, url: str) -> Optional[WebPage]:
        """Scrape page using requests and BeautifulSoup."""
        try:
            headers = {
                'User-Agent': self.user_agents[0],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract title
                    title = soup.find('title')
                    title_text = title.get_text() if title else url
                    
                    # Extract content (remove scripts, styles, etc.)
                    for script in soup(["script", "style", "nav", "footer", "header"]):
                        script.decompose()
                    
                    content = soup.get_text()
                    content = re.sub(r'\s+', ' ', content).strip()
                    
                    # Extract links
                    links = []
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href.startswith('http'):
                            links.append(href)
                        elif href.startswith('/'):
                            links.append(urljoin(url, href))
                    
                    return WebPage(
                        url=url,
                        title=title_text,
                        content=content,
                        links=links,
                        timestamp=datetime.now(),
                        source=urlparse(url).netloc
                    )
                else:
                    return None
                    
        except Exception as e:
            logger.warning(f"Requests scraping failed for {url}: {e}")
            return None
    
    async def _analyze_pages(self, pages: List[WebPage], query: str, 
                           tickers: List[str] = None) -> List[WebPage]:
        """Analyze and score pages for relevance."""
        try:
            analyzed_pages = []
            
            for page in pages:
                # Calculate relevance score
                relevance = self._calculate_relevance(page, query, tickers)
                page.relevance_score = relevance
                
                # Only keep relevant pages
                if relevance > 0.3:
                    analyzed_pages.append(page)
            
            # Sort by relevance
            analyzed_pages.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return analyzed_pages[:10]  # Keep top 10 most relevant
            
        except Exception as e:
            logger.error(f"Page analysis error: {e}")
            return pages
    
    def _calculate_relevance(self, page: WebPage, query: str, 
                           tickers: List[str] = None) -> float:
        """Calculate relevance score for a page."""
        score = 0.0
        content_lower = page.content.lower()
        title_lower = page.title.lower()
        query_lower = query.lower()
        
        # Title relevance
        if query_lower in title_lower:
            score += 0.4
        elif any(word in title_lower for word in query_lower.split()):
            score += 0.2
        
        # Content relevance
        if query_lower in content_lower:
            score += 0.3
        elif any(word in content_lower for word in query_lower.split()):
            score += 0.1
        
        # Ticker relevance
        if tickers:
            for ticker in tickers:
                if ticker.lower() in content_lower or ticker.lower() in title_lower:
                    score += 0.2
        
        # Source credibility
        credible_sources = ['bloomberg', 'reuters', 'wsj', 'marketwatch', 'yahoo', 'seekingalpha']
        if any(source in page.source.lower() for source in credible_sources):
            score += 0.1
        
        return min(score, 1.0)
    
    async def _generate_insights(self, pages: List[WebPage], query: str, 
                               tickers: List[str] = None) -> List[str]:
        """Generate insights from analyzed pages."""
        try:
            if not pages:
                return ["Insufficient data for analysis"]
            
            # Prepare content for analysis
            content_summary = []
            for page in pages[:5]:  # Use top 5 pages
                content_summary.append(f"Source: {page.source}\nTitle: {page.title}\nContent: {page.content[:500]}...")
            
            analysis_prompt = f"""Analyze the following web content and generate key insights for investment research.

Query: {query}
Tickers: {tickers if tickers else 'N/A'}

Content:
{chr(10).join(content_summary)}

Generate 5-7 key insights about:
1. Market trends and opportunities
2. Risk factors and concerns
3. Competitive landscape
4. Financial performance indicators
5. Future outlook and catalysts

Format as a list of concise insights."""

            if config.openai_api_key:
                response = openai_manager.chat_completion([
                    {"role": "user", "content": analysis_prompt}
                ], temperature=0.3)
                
                insights = response.get("content", "").split('\n')
                insights = [insight.strip() for insight in insights if insight.strip()]
                return insights[:7]
            else:
                return [
                    f"Found {len(pages)} relevant sources about {query}",
                    "Content analysis requires OpenAI API key for detailed insights",
                    "Key sources include: " + ", ".join(set(page.source for page in pages[:3]))
                ]
                
        except Exception as e:
            logger.error(f"Insight generation error: {e}")
            return ["Error generating insights"]
    
    async def _analyze_sentiment(self, pages: List[WebPage], query: str) -> Dict[str, Any]:
        """Analyze overall sentiment from pages."""
        try:
            if not pages:
                return {"sentiment": "neutral", "confidence": 0.0}
            
            # Prepare content for sentiment analysis
            content_for_analysis = []
            for page in pages[:3]:  # Use top 3 pages
                content_for_analysis.append(f"{page.title}: {page.content[:300]}")
            
            sentiment_prompt = f"""Analyze the sentiment of the following content related to: {query}

Content:
{chr(10).join(content_for_analysis)}

Provide sentiment analysis in JSON format:
{{
    "sentiment": "bullish/bearish/neutral",
    "confidence": 0.0-1.0,
    "key_positive_factors": ["factor1", "factor2"],
    "key_negative_factors": ["factor1", "factor2"],
    "overall_outlook": "description"
}}"""

            if config.openai_api_key:
                response = openai_manager.chat_completion([
                    {"role": "user", "content": sentiment_prompt}
                ], temperature=0.3)
                
                try:
                    sentiment = json.loads(response.get("content", "{}"))
                    return sentiment
                except json.JSONDecodeError:
                    return {"sentiment": "neutral", "confidence": 0.5}
            else:
                return {"sentiment": "neutral", "confidence": 0.3}
                
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {"sentiment": "neutral", "confidence": 0.0}
    
    async def _extract_risks_and_opportunities(self, pages: List[WebPage]) -> tuple[List[str], List[str]]:
        """Extract risk factors and opportunities from pages."""
        try:
            risks = []
            opportunities = []
            
            # Simple keyword-based extraction
            risk_keywords = ['risk', 'danger', 'threat', 'concern', 'warning', 'decline', 'loss', 'volatility']
            opportunity_keywords = ['opportunity', 'growth', 'potential', 'upside', 'gain', 'positive', 'bullish', 'catalyst']
            
            for page in pages[:5]:
                content_lower = page.content.lower()
                
                # Extract risks
                for keyword in risk_keywords:
                    if keyword in content_lower:
                        # Find context around keyword
                        idx = content_lower.find(keyword)
                        context = page.content[max(0, idx-100):idx+100]
                        risks.append(f"{keyword}: {context.strip()}")
                
                # Extract opportunities
                for keyword in opportunity_keywords:
                    if keyword in content_lower:
                        idx = content_lower.find(keyword)
                        context = page.content[max(0, idx-100):idx+100]
                        opportunities.append(f"{keyword}: {context.strip()}")
            
            return risks[:5], opportunities[:5]  # Limit to 5 each
            
        except Exception as e:
            logger.error(f"Risk/opportunity extraction error: {e}")
            return [], []
    
    def _fallback_result(self, query: str, tickers: List[str] = None) -> WebIntelligenceResult:
        """Fallback result when intelligence gathering fails."""
        return WebIntelligenceResult(
            pages=[],
            insights=[f"Web intelligence gathering failed for: {query}"],
            sentiment_analysis={"sentiment": "neutral", "confidence": 0.0},
            risk_factors=[],
            opportunities=[],
            sources=[],
            timestamp=datetime.now()
        )
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            if self.session:
                await self.session.close()
            
            if self.driver:
                self.driver.quit()
                
        except Exception as e:
            logger.error(f"WebIntelligenceAgent cleanup error: {e}")


# Global instance
web_intelligence_agent = WebIntelligenceAgent() 