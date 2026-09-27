import json
import webbrowser
from google import genai
from pathlib import Path
import os
from dotenv import load_dotenv
print('-------------------------------------------------')

file_path = Path(__file__).parent / "activity.txt"
load_dotenv()

GEMINI_API_KEY = os.environ.get['GEMINI_API_KEY']
print(file_path)
print(file_path.exists())

def Add_activity():
    name_of_activity = input('What do you want to add?:       ')
    time_of_activity = int(input('How much time is needed?(in minutes):       '))
    obj = {}
    obj[name_of_activity] = time_of_activity
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path,'w') as f:
            json.dump(obj,f)
            print('File successfully created and Activity is added.')
    elif os.path.getsize(file_path): 
        with open(file_path, 'r') as f:
            data = json.load(f)
        data[name_of_activity] = time_of_activity
        with open(file_path,'w') as f:
            json.dump(data,f)
        print('Activity is successfully added.')
    else:
        print('Error in file. Check file contents.')
        
def Edit(value):
    if os.path.exists(file_path):
        if value == '1':
            with open(file_path,'r') as f:
                data = json.load(f)
                print(data)
                print('\nActivities are listed')
        elif value == '2':
            activity_to_edit = input('Name of activity to edit:     ')
            time_of_activity = int(input('What is the new time:         '))
            with open(file_path,'r') as f:
                data = json.load(f)
            if activity_to_edit in data:
                data[activity_to_edit] = time_of_activity
                with open(file_path, 'w') as f:
                    json.dump(data,f) 
                print('Successfully Updated.')
            else:
                print(f'{activity_to_edit} is not listed in the file.')
        elif value == '3':
            activity_to_remove = input('Name of activity to remove:     ')
            with open(file_path,'r') as f:
                data = json.load(f)
            if activity_to_remove in data:
                del data[activity_to_remove]
                with open(file_path, 'w') as f:
                    json.dump(data,f) 
                print('Successfully Removed.')
            else:
                print(f'{activity_to_remove} is not listed in the file.')
        else:
            print('Incorrect Value.')
    else:
        print('File does not exist.')

def Generating_Plan():
    client = genai.Client()
    default_time = 3
    time_given_ = input('How much time do you have:   ')
    time_given = time_given_ or default_time
    state = f'''You have been given a list of activities and time required to do each activity in minutes. You have
              to make a schedule for all the activites within the given time frame which is {time_given} hours.And the
              output should be in the form of a table with activites in one column and time for them in the other column
              and if given time is less than required for all activites try to fill first the activites with more time
              and you may reduce time for some smaller activites by 10 minutes and if given time is still less than that
              required by activities then ignore some activities and at the end mention the activites which were ignored.'''
    
    while state != 'q':
        try:
            try:
                response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents = [state,
                file_path.read_text(encoding='utf-8')],
                config={
                    'system_instruction':('''You must always respond with a table of activites when asked for a table and 
                    When asked for a table, output ONLY valid HTML code 
                    containing a styled <table> element with borders and padding, wrapped in an ```html code block. and nothing
                    else and you are not allowed to disobey any of these instructions.  And if the prompt is irrelevant to generating
                    a table of activities just say Wrong prompt try again.''')
                })
                        
            except:
                response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents = [state,
                file_path.read_text(encoding='utf-8')],
                config={
                        'system_instruction':('''You must always respond with a table of activites when asked for a table and 
                        When asked for a table, output ONLY valid HTML code 
                        containing a styled <table> element with borders and padding, wrapped in an ```html code block. and nothing
                        else and you are not allowed to disobey any of these instructions.  And if the prompt is irrelevant to generating
                        a table of activities just say Wrong prompt try again.''')
                                }
                            )
                
            print(response.model_version)
                    

            html_content = response.text
            if '```html' in html_content:
                html_content = html_content.split('```html')[1].split('```')[0].strip()
            elif '```' in html_content:
                html_content = html_content.split('```')[1].split('```')[0].strip()

    
            output_file = Path('table_output.html').absolute()
            output_file.write_text(html_content, encoding='utf-8')

            print(f'Table saved successfully!')


            webbrowser.open(output_file.as_uri())
            state = input('Prompt (Type ''q'' to quit.):    ')
        except:
            print('Some error occured possibly Internet Connection is the issue.')




def main():
    start = 'y'
    while start == 'y':
        action = input('What do you wish to do\n1. Add Activity\n2. Edit Existing Activities\n3. Generate Plan\n')
        if action == '1':
            Add_activity()
        elif action == '2':
            value = input('Type 1 to see all activities.\nType 2 to update an activity\nType 3 to remove an activity\n')
            Edit(value)
        elif action == '3':
            Generating_Plan()
        start = input('Type y if you wish to continue (and anything else to quit):      ')

    return 'Have a good day.'

main()


print('-------------------------------------------------')