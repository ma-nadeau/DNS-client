# DNS Client Program (Python 3.12)

## Description

This Python program was developed using Python 3.12 which implements a DNS client software

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

## How to Run ##

### 1. Navigate to the `src` folder: ###
   ```bash
   cd src
   ```

### 2. To execute a DNS request, use the following command: ###
   ``` bash
   python dnsClient.py [-t timeout] [-r max-retries] [-p port] [-mx | -ns] @serverIPV4 domainName 
   ```

   - `timeout`: (Optional) How long to wait, in seconds, before retransmitting an unanswered query. **Default value: 5**.
   - `max-retries`: (Optional) The maximum number of retry attempts. **Default value: 3**.
   - `port`: (Optional) The UDP port number of the DNS server. **Default value: 53**.
   - `-mx | -ns flags`: (Optional) Indicates either to send a MX (Mail server) or NS (Name Server) query. At most one of these can be given, and **If neither is given then the client should a type A (IP Address) query**.
   - `@serverIPV4`: (Required) The IPv4 address of the DNS server, in a.b.c.d. format.
   - `domainName`: (Required) The domain name to query for.

### Example
``` bash
    python dnsClient.py -t 5 -r 3 -p 53 -ns @8.8.8.8 mcgill.ca 
```