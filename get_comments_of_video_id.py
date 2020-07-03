import argparse
import json
import pandas as pd

from apiclient.discovery import build
from csv import writer
from urllib.parse import urlparse, parse_qs

def get_keys(filename):
    with open(filename) as f:
        key = f.readline()
    DEVELOPER_KEY = key
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    return {'key': key, 'name': 'youtube', 'version': 'v3'}

def build_service(filename):
    with open(filename) as f:
        key = f.readline()

    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    return build(YOUTUBE_API_SERVICE_NAME,
                 YOUTUBE_API_VERSION,
                 developerKey=key)

def get_videos(**kwargs):
    final_results = []
    service = kwargs['service']

    kwargs['part'] = kwargs.get('part', 'id,snippet')

    search_response = service.videos().list(
        **kwargs
    ).execute()

    i = 0
    max_pages = 3
    while search_response and i < max_pages:
        final_results.extend(search_response['items'])

        if 'nextPageToken' in search_response:
            kwargs['pageToken'] = search_response['nextPageToken']
            search_response = service.search().list(
                **kwargs
                ).execute()
            i += 1
        else:
            break
    return final_results

# https://stackoverflow.com/questions/45579306/get-youtube-video-url-or-youtube-video-id-from-a-string-using-regex
def get_id(url):
    u_pars = urlparse(url)
    quer_v = parse_qs(u_pars.query).get('v')
    if quer_v:
        return quer_v[0]
    pth = u_pars.path.split('/')
    if pth:
        return pth[-1]

def get_comments(**kwargs):
    """
    ty: 
    https://python.gotrained.com/youtube-api-extracting-comments/#Cache_Credentials
    https://www.pingshiuanchua.com/blog/post/using-youtube-api-to-analyse-youtube-comments-on-python
    """
    comments, commentsId, repliesCount, likesCount, viewerRating = [], [], [], [], []

    # clean kwargs
    kwargs['part'] = kwargs.get('part', 'snippet')
    kwargs['maxResults'] = kwargs.get('maxResults', 100)
    kwargs['textFormat'] = kwargs.get('textFormat', 'plainText')
    kwargs['order'] = kwargs.get('order', 'time')
    iterations = kwargs.pop('iterations', None)
    write_lbl = kwargs.pop('write_lbl', True)
    csv_filename = kwargs.pop('csv_filename')
    token_filename = kwargs.pop('token_filename')
    service = kwargs.pop('service')
    
    response = service.commentThreads().list(
        **kwargs
    ).execute()

    while response:
        if iterations and count == iterations:
            return {
                'Comments': comments,
                'Comment ID' : commentsId,
                'Reply Count' : repliesCount,
                'Like Count' : likesCount,
                'Commenter Rating Video' : viewerRating
                }

        index = 0
        for item in response['items']:
            print(f"comment {index}")
            index += 1
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comment_id = item['snippet']['topLevelComment']['id']
            reply_count = item['snippet']['totalReplyCount']
            like_count = item['snippet']['topLevelComment']['snippet']['likeCount']

            viewer_rating = None
            
            comments.append(comment)
            commentsId.append(comment_id)
            repliesCount.append(reply_count)
            likesCount.append(like_count)
            viewerRating.append(viewer_rating)

            if write_lbl == True:
                with open(f'{csv_filename}.csv', 'a+') as f:
                    # https://thispointer.com/python-how-to-append-a-new-row-to-an-existing-csv-file/#:~:text=Open%20our%20csv%20file%20in,in%20the%20associated%20csv%20file
                    csv_writer = writer(f)
                    csv_writer.writerow([comment, comment_id, reply_count, like_count, viewer_rating])

            if 'nextPageToken' in response:

                with open(f'{token_filename}.txt', 'a+') as f:
                    f.write(kwargs.get('pageToken', ''))
                    f.write('\n')
                kwargs['pageToken'] = response['nextPageToken']
                response = service.commentThreads().list(
                    **kwargs
                ).execute()
            else:
                return {
                    'Comments': comments,
                    'Comment ID' : commentsId,
                    'Reply Count' : repliesCount,
                    'Like Count' : likesCount,
                    'Commenter Rating Video' : viewerRating
                }

def save_to_csv(output_dict, video_id, output_filename):
    output_df = pd.DataFrame(output_dict, columns = output_dict.keys())
    output_df.to_csv(f'{output_filename}.csv')

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--part', help='Desired properties of commentThread', default='snippet')
    parser.add_argument('--maxResults', help='Max results per page', default=100)
    parser.add_argument('--iterations', help='How many pages to parse', default=None)
    parser.add_argument('--write_lbl', help="Update csv after each comment?", default=True)
    parser.add_argument('--csv_filename', default=None)
    parser.add_argument('--token_filename', default=None)
    parser.add_argument('--video_url', default='https://www.youtube.com/watch?v=ioNng23DkIM')
    parser.add_argument('--order', default='time')
    parser.add_argument('--apikey', default='../apikey.json')
    args = parser.parse_args()

    service = build_service(args.apikey)
    video_id = get_id(args.video_url)

    if not args.csv_filename:
        args.csv_filename = video_id + "_csv"

    if not args.token_filename:
        args.token_filename = video_id + "_page_token"

    kwargs = vars(args)
    kwargs.pop('apikey')
    kwargs.pop('video_url')
    kwargs['videoId'] = video_id
    kwargs['service'] = service
    output_dict = get_comments(**kwargs)

    args.csv_filename += "_final"
    save_to_csv(output_dict, video_id, args.csv_filename)
    
if __name__ == '__main__':
    # do the things
    main()



response = service.commentThreads().list(
    part='snippet',
    maxResults=100,
    textFormat='plainText',
    order='time',
    videoId='ioNng23DkIM',
    nextPageToken=response['nextPageToken']
  ).execute()
