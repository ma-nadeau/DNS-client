Python program that implements a DNS client software

This DNS client is capable of sending queries for:
- A records (IP addresses)
- MX records (mail server)
- NS records (name server)
And interpreting responses for:
- A records
- CNAME records

The program is responsible for:
- Parsing the user input (if the program is invoked from the command line/stdin)
- Sending queries to the server for the domain name using UDP sockets
- Receiving the response from the server (and resending other queries if needed)
- Interpreting the response form the server and outputing the result to the terminal display (stdout if the program is invoked from the command line)