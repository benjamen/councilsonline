# Page snapshot

```yaml
- generic [ref=e5]:
  - generic [ref=e6]:
    - img [ref=e8]
    - heading "Welcome Back" [level=1] [ref=e10]
    - paragraph [ref=e11]: Sign in to your Lodgeick account
  - generic [ref=e12]:
    - generic [ref=e13]:
      - generic [ref=e14]:
        - generic [ref=e15]: Email or Username
        - textbox "Email or Username" [ref=e18]:
          - /placeholder: Administrator or you@example.com
      - generic [ref=e19]:
        - generic [ref=e20]:
          - generic [ref=e21]: Password
          - link "Forgot password?" [ref=e22] [cursor=pointer]:
            - /url: "#"
        - textbox "Password" [ref=e25]:
          - /placeholder: Enter your password
      - generic [ref=e26]:
        - checkbox "Remember me for 30 days" [ref=e27]
        - generic [ref=e28]: Remember me for 30 days
      - button "Sign In" [ref=e29] [cursor=pointer]:
        - generic [ref=e30]: Sign In
    - generic [ref=e35]: or
    - button "Continue with Google" [ref=e37] [cursor=pointer]:
      - img [ref=e38]
      - text: Continue with Google
  - paragraph [ref=e44]:
    - text: Don't have an account?
    - link "Create one now" [ref=e45] [cursor=pointer]:
      - /url: /frontend/account/register
  - link "Back to home" [ref=e47] [cursor=pointer]:
    - /url: /frontend/
    - img [ref=e48]
    - text: Back to home
```