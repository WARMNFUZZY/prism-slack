import os

def deadline_submission_script(core, output, state_data, prism_user):
    root = os.path.join(core.prismRoot, "Scripts")
    root = root.replace("\\", "/")
    project = state_data["project"]

    code = f"""
import os
import sys
sys.path.append("{root}")
import PrismCore

pcore = PrismCore.create(prismArgs=["noUI", "{project}"])

slack = pcore.getPlugin('Slack')

slack.publish_to_slack(r"{output}", {state_data}, r"{prism_user}")
"""

    return code
