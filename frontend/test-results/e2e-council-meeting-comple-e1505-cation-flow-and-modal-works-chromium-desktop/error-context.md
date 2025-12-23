# Page snapshot

```yaml
- generic [ref=e4]:
  - banner [ref=e5]:
    - generic [ref=e8]:
      - button "Go back" [ref=e9] [cursor=pointer]:
        - img [ref=e10]
      - heading "New Application" [level=1] [ref=e13]
  - generic [ref=e20]:
    - generic [ref=e21]: Council
    - generic [ref=e22]: 25% Complete
  - main [ref=e23]:
    - generic [ref=e26]:
      - heading "Select Council" [level=2] [ref=e27]
      - paragraph [ref=e28]: Choose the council that will process your application
      - generic [ref=e30]: lodgeick.api.get_active_councils ValidationError
    - generic [ref=e31]:
      - button "Next" [ref=e34] [cursor=pointer]:
        - generic [ref=e35]: Next
        - img [ref=e36]
      - paragraph [ref=e39]: Your progress is automatically saved. You can return to complete this application later.
```