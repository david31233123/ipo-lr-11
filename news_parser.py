import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os


def parse_hacker_news():
    """
    Парсит новости с Hacker News
    Возвращает список словарей с заголовками, ссылками и количеством комментариев
    """
    url = "https://news.ycombinator.com/"
    
    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка при получении страницы: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Находим все строки с заголовками и мета-информацией
    titles = soup.find_all('span', class_='titleline')
    subtexts = soup.find_all('td', class_='subtext')
    
    news_list = []
    
    for i, (title, subtext) in enumerate(zip(titles, subtexts), 1):
        try:
            # Извлекаем заголовок
            title_link = title.find('a')
            news_title = title_link.text.strip()
            news_url = title_link.get('href', '')
            
            # Извлекаем количество комментариев
            comments_elem = subtext.find_all('a')[-1]
            comments_text = comments_elem.text
            
            # Преобразуем "discuss" или "N comments" в число
            if 'comment' in comments_text:
                # Извлекаем число из строки "N comments"
                comments = int(comments_text.split()[0])
            elif 'discuss' in comments_text:
                comments = 0
            else:
                comments = 0
            
            # Извлекаем рейтинг, если есть
            score_elem = subtext.find('span', class_='score')
            score = int(score_elem.text.split()[0]) if score_elem else 0
            
            # Извлекаем автора
            author_elem = subtext.find('a', class_='hnuser')
            author = author_elem.text if author_elem else "Unknown"
            
            news_list.append({
                'id': i,
                'title': news_title,
                'url': news_url if news_url.startswith('http') else f'https://news.ycombinator.com/{news_url}',
                'comments': comments,
                'score': score,
                'author': author,
                'hn_url': f'https://news.ycombinator.com/item?id={title_link.find_parent("tr").find_next_sibling("tr").get("id", "")}'
            })
            
        except Exception as e:
            print(f"Ошибка при обработке новости {i}: {e}")
            continue
    
    return news_list


def save_to_json(news_data, filename='data.json'):
    """Сохраняет данные в JSON файл"""
    data = {
        'last_updated': datetime.now().isoformat(),
        'source': 'https://news.ycombinator.com/',
        'news_count': len(news_data),
        'news': news_data
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Данные сохранены в {filename}")
    return filename


def print_news_to_console(news_data):
    """Выводит новости в консоль в требуемом формате"""
    print("\n" + "="*60)
    print("НОВОСТИ С HACKER NEWS")
    print("="*60)
    
    for news in news_data[:10]:  # Выводим первые 10 новостей
        print(f"{news['id']}. Title: {news['title'][:50]}...; Comments: {news['comments']};")
    
    print(f"\nВсего новостей: {len(news_data)}")
    print("="*60)


def generate_html(news_data, filename='index.html'):
    """Генерирует HTML страницу с таблицей новостей"""
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hacker News Parser</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .container {{
            max-width: 1200px;
            width: 100%;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            padding: 30px;
            margin-top: 20px;
            backdrop-filter: blur(10px);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            color: white;
        }}
        
        h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }}
        
        .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: flex;
            justify-content: space-between;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 2px solid #e9ecef;
        }}
        
        .stat-item {{
            text-align: center;
            flex: 1;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .news-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .news-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: left;
            font-size: 1.1em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .news-table td {{
            padding: 18px 20px;
            border-bottom: 1px solid #e9ecef;
            transition: all 0.3s ease;
        }}
        
        .news-table tr:hover td {{
            background: #f8f9fa;
            transform: translateY(-2px);
        }}
        
        .news-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .news-title {{
            font-weight: 600;
            color: #333;
            font-size: 1.1em;
            line-height: 1.4;
        }}
        
        .news-title a {{
            color: inherit;
            text-decoration: none;
            transition: color 0.3s ease;
        }}
        
        .news-title a:hover {{
            color: #667eea;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 10px;
        }}
        
        .comments-badge {{
            background: #4CAF50;
            color: white;
        }}
        
        .score-badge {{
            background: #FF9800;
            color: white;
        }}
        
        .author {{
            color: #666;
            font-style: italic;
        }}
        
        .source-link {{
            display: inline-block;
            margin-top: 30px;
            padding: 12px 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 600;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .source-link:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        .last-updated {{
            text-align: right;
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            
            h1 {{
                font-size: 2em;
            }}
            
            .news-table {{
                font-size: 0.9em;
            }}
            
            .news-table th,
            .news-table td {{
                padding: 12px 10px;
            }}
            
            .stats {{
                flex-direction: column;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 Hacker News Parser</h1>
            <div class="subtitle">Latest stories from the tech community</div>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(news_data)}</div>
                <div>Total Stories</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{sum(news['comments'] for news in news_data)}</div>
                <div>Total Comments</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{max(news['score'] for news in news_data) if news_data else 0}</div>
                <div>Highest Score</div>
            </div>
        </div>
        
        <div class="last-updated">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        <table class="news-table">
            <thead>
                <tr>
                    <th width="5%">#</th>
                    <th width="55%">Title</th>
                    <th width="15%">Author</th>
                    <th width="10%">Score</th>
                    <th width="15%">Comments</th>
                </tr>
            </thead>
            <tbody>
"""

    # Добавляем строки таблицы
    for news in news_data:
        html_template += f"""
                <tr>
                    <td><strong>{news['id']}</strong></td>
                    <td class="news-title">
                        <a href="{news['url']}" target="_blank" rel="noopener noreferrer">
                            {news['title']}
                        </a>
                    </td>
                    <td class="author">{news['author']}</td>
                    <td>
                        <span class="badge score-badge">▲ {news['score']}</span>
                    </td>
                    <td>
                        <span class="badge comments-badge">💬 {news['comments']}</span>
                    </td>
                </tr>
"""

    html_template += f"""
            </tbody>
        </table>
        
        <div class="footer">
            <a href="https://news.ycombinator.com/" class="source-link" target="_blank" rel="noopener noreferrer">
                🔗 Visit Original Hacker News
            </a>
            <p style="margin-top: 15px;">
                Generated by Hacker News Parser • Data is updated automatically
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"HTML страница создана: {filename}")
    return filename


def main():
    """Основная функция программы"""
    print("🔍 Начинаю парсинг Hacker News...")
    
    # Парсим новости
    news_data = parse_hacker_news()
    
    if not news_data:
        print("❌ Не удалось получить новости")
        return
    
    # Выводим в консоль
    print_news_to_console(news_data)
    
    # Сохраняем в JSON
    json_file = save_to_json(news_data)
    
    # Генерируем HTML
    html_file = generate_html(news_data)
    
    print("\n" + "="*60)
    print("✅ Задание выполнено!")
    print("="*60)
    print(f"1. Новости выведены в консоль")
    print(f"2. Данные сохранены в: {json_file}")
    print(f"3. HTML страница создана: {html_file}")
    print("\nОткройте файл index.html в браузере для просмотра результата")
    print("="*60)


if __name__ == "__main__":
    main()