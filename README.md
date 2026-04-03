Author: Minh Khang Nguyen
Date: 03/04/2026

--This is the guide to run our demo.
1. Please create a new conda environment and install our requirements.txt
2. To run, frontend, please move to frontend/my-fe.
3. Open your browser and install nodejs https://nodejs.org/en/download/current (if you are using Window, please find the window installer, if you are using MacOS, please find the Mac Install. These should be green bottons below the Bash/terminal/cmd window)
4. After installing NodeJs. Please go back to frontend/my-fe.
5. Open your terminal at this directory, and run: npm run dev
    You should have something like this:
    > my-fe@0.1.0 dev
    > next dev

    ▲ Next.js 16.2.1 (Turbopack)
    - Local:         http://localhost:3000
    - Network:       http://192.168.8.200:3000
    ✓ Ready in 206ms
6. To open the UI, please look at the terminal and click the link of local http://localhost:3000
7. The UI will appear on your browser.
8. To run the flask backend,
9. Redirect to ragbot folder.
10. Open the .env file (this file is added after I pull this from one of our github branch, because of gitignore, so this is added manually)
11. Go this link https://aistudio.google.com/prompts/new_chat
12. Find the "Get API key" at the bottom left corner.
13. Create one API by cliking the import projects.
14. Then, get that API and past to the first part of the .env file
15. To get API for LANGSMITH_API_KEY
16. Go to https://smith.langchain.com/ and login to your account or create one (if you don't have an account)
17. Once, you login, find the "Tracing" on the left vertical bar.
18. Click on it, and click "+Project", and give it a name, here we put "new_test" for example.
19. LangSmith takes you to a portal, on the top please choose "Google Gemini"
20. Then press "Generate API Key"
21. Copy that API and paste it to LANGSMITH_API_KEY= in the .env file.
22. For TAVILY_API_KEY=
23. Open to https://www.tavily.com/
24. login to your account or create one (if you don't have an account)
25. In the main portal, please find the "API keys" card in the main page.
26. Click the "plus" icon next to API Keys.
27. Choose dev option with limit of 1000 monthly usage, and click create.
28. Copy the API and paste it to TAVILY_API_KEY= in .env
29. for PINECONE_API_KEY=
30. Please go to https://www.pinecone.io/
31. login to your account or create one (if you don't have an account)
32. Once after you login, find "Databases" on left vertical bar.
33. Then cliks "Indexes"
34. Then click "Create Index" on the right margin
35. Then, you give you index a name, for example "testing"
36. In the configuration "Scroll horizontally to find Config manually", select vector type is Dense, Dimension is 1536, and Metric is Consine.
37. Choose cloud provider is AWS.
38. Region is us-eat Virginia
39. Then click "Create index" (As we are using start plan, only the first one is free)
40. go back to "Indexes", once we create it, it will give an API.
41. Copy and paste that to PINECONE_API_KEY=
42. The index name is the name we gave while we creating this in Pinecone which is "testing" in point(35)
43. After this, open your terminal with the activated conda env.
44. We need to run the ingestion.py first. Make sure the data file sample "A1-QandA.txt" is in the same place. This helps you load, split, and embed the data to Pinecone.
45. Then, run the controller.py
46. Then, you can go back to the running fronttend and interact with the system.



