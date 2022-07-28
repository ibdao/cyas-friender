1) write a route that accepts ability of a user to submit a photo

2a) create forms
2b) create templates for html

3) create routes 

4) create users 

5) find a way to display photos
    This will have to include fetching photo from AWS 
    by finding the file name that matches the database
    <img src="http://friender-bucket-r26-ian/{img_file}" />

6) build nav bar to go back home. 
    home will show other users
    query the data base to get other users user.id !== self (the person logged in aka g.user)
    show their pictures on home page user.img_url. 

    for loop to loop over what we queried
        <img src="user.img_url">
        other info
