## Harvest project
Harvest project aims to make learning visible to educators and decision makers.
Within the context of the Sugar Learning Platform, this can be achieved by
collecting reliable metadata from the Journal.

## Harvest client setup

1. Get the harvest-client:

        $cd /path/to/somewhere/
        $git clone https://github.com/tchx84/harvest-client.git
        $cd harvest-client

2. Install the harvest-client:

        $cp -r extensions ~/.sugar/default/

3. Restart Sugar.

4. Go the web accounts section at the control panel.

5. Complete the server information and click on the collect button.

## Automatic collection

* In order to enable automatic collection:

        $cd /path/to/somewhere/harvest-client/
        $cp etc/harvest-collect-ifup /etc/NetworkManager/dispatcher.d/

## More Information

If you just want to use this, I recommend you to read the
wiki documentation at http://wiki.sugarlabs.org/go/Harvest
