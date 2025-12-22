# Page snapshot

```yaml
- generic [ref=e1]:
  - navigation [ref=e2]:
    - generic [ref=e3]:
      - link "Home" [ref=e4] [cursor=pointer]:
        - /url: /
      - generic:
        - list
  - main [ref=e7]:
    - generic [ref=e10]:
      - generic [ref=e11]:
        - img [ref=e12]
        - heading "Login to Frappe" [level=4] [ref=e13]
      - form [ref=e15]:
        - generic [ref=e16]:
          - generic [ref=e17]:
            - generic [ref=e18]:
              - generic [ref=e19]: Email
              - generic [ref=e20]:
                - textbox "Email" [active] [ref=e21]:
                  - /placeholder: jane@example.com
                - img [ref=e22]
            - generic [ref=e24]:
              - generic [ref=e25]: Password
              - generic [ref=e26]:
                - textbox "Password" [ref=e27]:
                  - /placeholder: •••••
                - img [ref=e28]
                - generic [ref=e30] [cursor=pointer]: Show
            - paragraph [ref=e31]:
              - link "Forgot Password?" [ref=e32] [cursor=pointer]:
                - /url: "#forgot"
          - button "Login" [ref=e34] [cursor=pointer]
          - generic [ref=e35]:
            - paragraph [ref=e36]: or
            - link "Login with Email Link" [ref=e39] [cursor=pointer]:
              - /url: "#login-with-email-link"
```