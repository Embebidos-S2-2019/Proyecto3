#include <sys/mman.h> //mmap
#include <err.h>      //error handling
#include <fcntl.h>    //file ops
#include <unistd.h>   //usleep

#define HIGH 1
#define LOW 0

typedef enum
{
    INPUT = 0x0,
    OUTPUT = 0x1,
    FUNC0 = 0x4,
    FUNC1 = 0x5,
    FUNC2 = 0x6,
    FUNC3 = 0x7,
    FUNC4 = 0x3,
    FUNC5 = 0x2
} pin_modes;

//Static base
static unsigned GPIO_BASE = 0x3f200000;
//Regs pointers
volatile unsigned int *gpfsel0;
volatile unsigned int *gpset0;
volatile unsigned int *gpclr0;
volatile unsigned int *gplvl0;
/*Function prototypes*/
void gpioInitPtrs();
void gpioSetMode(int pin, pin_modes mode);
void gpioGroupSetMode(int *pins, int size, pin_modes mode);
void gpioWrite(int pin, unsigned char bit);
int gpioRead(int pin);

//Initialize pointers: performs memory mapping, exits if mapping fails
void gpioInitPtrs()
{
    int fd = -1;
    //Loading /dev/mem into a file
    if ((fd = open("/dev/mem", O_RDWR, 0)) == -1)
        err(1, "Error opening /dev/mem");
    //Mapping GPIO base physical address
    gpfsel0 = (unsigned int *)mmap(0, getpagesize(),
                                   PROT_WRITE, MAP_SHARED, fd, GPIO_BASE);
    //Check for mapping errors
    if (gpfsel0 == MAP_FAILED)
        errx(1, "Error during mapping GPIO");
    //Set regs pointers
    gpset0 = gpfsel0 + 0x7; // offset 0x1C / 4 = 0x7
    gpclr0 = gpfsel0 + 0xA; // offset 0x28 / 4 = 0xA
    gplvl0 = gpfsel0 + 0xD; // offset 0x34 / 5 = 0xD
}
//Sets GPIO pin as pin mode
void gpioSetMode(int pin, pin_modes mode)
{
    int sel_reg = pin / 10;                    //the sel[n] register to set
    int sel_offset = (pin - 10 * sel_reg) * 3; // register offset

    //pointer to the correct funciton select register
    volatile unsigned int *gpfsel_reg = gpfsel0 + sel_reg;

    //does not check the function matches the PIN
    //set the mode bits to the correct pin by moving it to it's offset
    *gpfsel_reg = *gpfsel_reg | mode << sel_offset;
}

//Sets GPIO pins as mode to the group of pins pointed to by pins
void gpioGroupSetMode(int *pins, int size, pin_modes mode)
{
    for (int i = 0; i < size; ++i)
    {
        gpioSetMode(pins[i], mode);
    }
}

//Writes to to the GPIO pin specified by pin the value in bit (0,1)
void gpioWrite(int pin, unsigned char bit)
{
    int reg = pin / 32;          //the sel[n] register to set
    int offset = pin - 32 * reg; // register offset

    //pointer to the correct set/clear  register
    volatile unsigned int *gpfset_reg = gpset0 + reg;
    volatile unsigned int *gpfclr_reg = gpclr0 + reg;
    if (bit)
        *gpfset_reg = *gpfset_reg | (1 << offset); //sets bit
    else
        *gpfclr_reg = *gpfclr_reg | (1 << offset); //clears bit
}

void gpioBulkWrite(int *pins, int size, unsigned char bit)
{
    for (int i = 0; i < size; ++i)
    {
        gpioWrite(pins[i], bit);
    }
}

//Reads the value of the pin specified by pin
int gpioRead(int pin)
{
    int reg = pin / 32;          //the sel[n] register to set
    int offset = pin - 32 * reg; // register offset
    //pointer to the correct level register
    volatile unsigned int *gpflvl_reg = gplvl0 + reg;

    int lvl = *gpflvl_reg & (1 << offset);
    if (lvl)
        return HIGH;
    else
        return LOW;
}

// int main(int argc, char const *argv[])
// {
//     gpioInitPtrs();
//     // pin_modes mode = OUTPUT;
//     gpioSetMode(2, OUTPUT);

//     //toggle GPIO2
//     gpioWrite(2, 1);
//     usleep(1000000);
//     gpioWrite(2, 0);
//     return 0;
// }