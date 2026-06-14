# weechat-icat

A WeeChat script for displaying images in the chat.

Requires support for the [kitty terminal graphics
protocol](https://sw.kovidgoyal.net/kitty/graphics-protocol/) with support for
unicode placeholders. At the time of writing only the development version of
[kitty](https://sw.kovidgoyal.net/kitty/) supports this.

Requires PIL (Python Imaging Library) or [Pillow](https://pillow.readthedocs.io/en/stable/).

## Automatically previewing uploaded images in Slack using [wee-slack](https://github.com/wee-slack/wee-slack/)

Add the following trigger, adjusting anything as necessary:

```
/trigger addreplace icat_slack print "" "${tg_message} =~ https://files\.slack\.com/[^ ]*\.(png|jpg|jpeg|gif|webp)" ",.*(https://files\.slack\.com/[^ ]*).*,${re:1}," "/icat -auth ${plugins.var.python.slack.slack_api_token} -print_immediately -columns 80 -rows 20 -quiet ${tg_message}"
```
