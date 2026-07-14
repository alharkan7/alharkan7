import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('GITHUB_TOKEN')
USERNAME = os.getenv('GITHUB_USER', 'alharkan7')

def fetch_stats():
    if not TOKEN:
        print("github_token not found in .env")
        return None
        
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    query = """
    query($login: String!) {
      user(login: $login) {
        followers { totalCount }
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          nodes {
            stargazerCount
          }
        }
        repositoriesContributedTo(first: 1, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {
          totalCount
        }
      }
    }
    """
    
    response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': {'login': USERNAME}}, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching stats: {response.text}")
        return None
        
    data = response.json()
    if 'errors' in data:
        print(f"GraphQL Errors: {data['errors']}")
        return None
        
    user = data['data']['user']
    
    followers = user['followers']['totalCount']
    repos = user['repositories']['totalCount']
    stars = sum(repo['stargazerCount'] for repo in user['repositories']['nodes'])
    contributed = user['repositoriesContributedTo']['totalCount']
    
    return {
        'repo_data': f"{repos:,}",
        'star_data': f"{stars:,}",
        'follower_data': f"{followers:,}",
        'contrib_data': f"{contributed:,}",
    }

def align_line(line):
    # LOC formatting
    if 'Lines of Code on GitHub' in line:
        # We need to ensure no spacing in brackets: (123++, 345--)
        # The structure is: ... <tspan class="value" id="loc_data">VAL</tspan> (<tspan class="addColor" id="loc_add">ADD</tspan><tspan class="addColor">++</tspan>, <tspan class="delColor" id="loc_del">DEL</tspan><tspan class="delColor">--</tspan>)
        # We'll just replace the whole line cleanly
        
        loc_match = re.search(r'<tspan class="value" id="loc_data">([^<]+)</tspan>', line)
        add_match = re.search(r'<tspan class="addColor" id="loc_add">([^<]+)</tspan>', line)
        del_match = re.search(r'<tspan class="delColor" id="loc_del">([^<]+)</tspan>', line)
        
        loc_val = loc_match.group(1) if loc_match else '0'
        add_val = add_match.group(1) if add_match else '0'
        del_val = del_match.group(1) if del_match else '0'
        
        left_text = '. Lines of Code on GitHub:'
        right_text = f'{loc_val} ({add_val}++, {del_val}--)'
        dots_needed = 60 - len(left_text) - len(right_text)
        dots = " " + "." * max(0, dots_needed - 2) + " " if dots_needed >= 2 else " "
        
        return f'<tspan x="15" y="490" class="cc">. </tspan><tspan class="key">Lines of Code on GitHub</tspan>:<tspan class="cc" id="loc_data_dots">{dots}</tspan><tspan class="value" id="loc_data">{loc_val}</tspan> (<tspan class="addColor" id="loc_add">{add_val}</tspan><tspan class="addColor">++</tspan>, <tspan class="delColor" id="loc_del">{del_val}</tspan><tspan class="delColor">--</tspan>)'
        
    if '|' in line and 'id="repo_data_dots"' in line:
        repo_match = re.search(r'<tspan class="value" id="repo_data">([^<]+)</tspan>', line)
        contrib_match = re.search(r'<tspan class="value" id="contrib_data">([^<]+)</tspan>', line)
        star_match = re.search(r'<tspan class="value" id="star_data">([^<]+)</tspan>', line)
        
        repo_val = repo_match.group(1) if repo_match else '0'
        contrib_val = contrib_match.group(1) if contrib_match else '0'
        star_val = star_match.group(1) if star_match else '0'
        
        left_text = '. Repos:'
        mid1_text = f'{repo_val} {{Contributed: {contrib_val}}} '
        
        pipe_pos = 40 # index of pipe
        dots1_needed = pipe_pos - len(left_text) - len(mid1_text)
        dots1 = " " + "." * max(0, dots1_needed - 2) + " " if dots1_needed >= 2 else " "
        
        right_text = ' Stars:'
        dots2_needed = 60 - 41 - len(right_text) - len(star_val)
        dots2 = " " + "." * max(0, dots2_needed - 2) + " " if dots2_needed >= 2 else " "
        
        return f'<tspan x="15" y="450" class="cc">. </tspan><tspan class="key">Repos</tspan>:<tspan class="cc" id="repo_data_dots">{dots1}</tspan><tspan class="value" id="repo_data">{repo_val}</tspan> {{<tspan class="key">Contributed</tspan>: <tspan class="value" id="contrib_data">{contrib_val}</tspan>}} | <tspan class="key">Stars</tspan>:<tspan class="cc" id="star_data_dots">{dots2}</tspan><tspan class="value" id="star_data">{star_val}</tspan>'
        
    if '|' in line and 'id="commit_data_dots"' in line:
        commit_match = re.search(r'<tspan class="value" id="commit_data">([^<]+)</tspan>', line)
        follower_match = re.search(r'<tspan class="value" id="follower_data">([^<]+)</tspan>', line)
        
        commit_val = commit_match.group(1) if commit_match else '0'
        follower_val = follower_match.group(1) if follower_match else '0'
        
        left_text = '. Commits:'
        mid1_text = f'{commit_val} '
        
        pipe_pos = 40
        dots1_needed = pipe_pos - len(left_text) - len(mid1_text)
        dots1 = " " + "." * max(0, dots1_needed - 2) + " " if dots1_needed >= 2 else " "
        
        right_text = ' Followers:'
        dots2_needed = 60 - 41 - len(right_text) - len(follower_val)
        dots2 = " " + "." * max(0, dots2_needed - 2) + " " if dots2_needed >= 2 else " "
        
        return f'<tspan x="15" y="470" class="cc">. </tspan><tspan class="key">Commits</tspan>:<tspan class="cc" id="commit_data_dots">{dots1}</tspan><tspan class="value" id="commit_data">{commit_val}</tspan> | <tspan class="key">Followers</tspan>:<tspan class="cc" id="follower_data_dots">{dots2}</tspan><tspan class="value" id="follower_data">{follower_val}</tspan>'

    match = re.match(r'^(.*?)(<tspan class="cc"(?: id="[\w_]+")?>) \.+ (</tspan>)(.*?)$', line)
    if not match:
        return line
        
    left_xml = match.group(1)
    dots_start = match.group(2)
    dots_end = match.group(3)
    right_xml = match.group(4)
    
    left_text = re.sub(r'<[^>]+>', '', left_xml)
    right_text = re.sub(r'<[^>]+>', '', right_xml)
    
    total_len = len(left_text) + len(right_text)
    dots_needed = 60 - total_len
    
    if dots_needed < 2:
        return line
        
    new_dots = " " + "." * (dots_needed - 2) + " "
    return f'{left_xml}{dots_start}{new_dots}{dots_end}{right_xml}'

def update_svg(filepath, stats):
    with open(filepath, 'r') as f:
        lines = f.read().split('\n')
        
    for i in range(len(lines)):
        # Update values if stats is provided
        if stats:
            for key, val in stats.items():
                pattern = r'(<tspan [^>]*id="' + key + r'">)[^<]+(</tspan>)'
                lines[i] = re.sub(pattern, r'\g<1>' + str(val) + r'\g<2>', lines[i])
            
        # Re-align lines
        if 'class="cc"' in lines[i] and ('....' in lines[i] or 'id=' in lines[i]):
            lines[i] = align_line(lines[i])
            
    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))
    print(f"Updated {filepath}")

def main():
    print("Fetching stats...")
    stats = fetch_stats()
    if not stats:
        print("Failed to fetch stats, but will re-align files anyway.")
        
    update_svg('dark_mode.svg', stats)
    update_svg('light_mode.svg', stats)

if __name__ == '__main__':
    main()
