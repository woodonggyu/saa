from typing import Optional
import boto3


class WAFv2:
    """AWS WAFv2 Service"""

    def __init__(self):
        """"""

        self.waf_v2 = boto3.client("wafv2")

    def get_ip_set(self, name: str, resource_id: str, scope: Optional[str] = "REGIONAL") -> dict:
        """Retrieves the specified IPSet"""

        parameters = {
            "Name": name,
            "Scope": scope,
            "Id": resource_id
        }

        return self.waf_v2.get_ip_set(**parameters)

    def update_ip_set(self, name: str, _id: str, addresses: list, token: str, scope: Optional[str] = "REGIONAL") \
            -> dict:
        """Updates the specified IPSet"""

        parameters = {
            "Name": name,
            "Scope": scope,
            "Id": _id,
            "Addresses": addresses,
            "LockToken": token
        }

        return self.waf_v2.update_ip_set(**parameters)


if __name__ == "__main__":
    waf = WAFv2()

    ip_set = waf.get_ip_set(name="IPSetsRule01", resource_id="b9f0509c-2c36-42f6-bf1f-92de1128d7ad")

    waf.update_ip_set(name="IPSetsRule01", _id=ip_set["IPSet"]["Id"], addresses=["2.2.2.2/32"],
                      token=ip_set["LockToken"])


